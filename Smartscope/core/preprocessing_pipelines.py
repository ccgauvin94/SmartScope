from abc import ABC, abstractmethod
from functools import partial
import time
from typing import List, Mapping, Union, Optional, Dict, Any
import os
import multiprocessing
import logging
import psutil
import subprocess as sub
import shlex
from pathlib import Path
from pydantic import BaseModel, Field, validator


from Smartscope.core.db_manipulations import websocket_update
from Smartscope.core.models import AutoloaderGrid
from Smartscope.lib.Datatypes.models import generate_unique_id
from Smartscope.lib.preprocessing_methods import get_CTFFIN4_data, process_hm_from_average, process_hm_from_frames, processing_worker_wrapper
from Smartscope.core.models.models_actions import update_fields
from Smartscope.core.settings.worker import DEFAULT_PREPROCESSING_PIPELINE
from Smartscope.lib.logger import add_log_handlers

from django.db import transaction
from django import forms


logger = logging.getLogger(__name__)


class PreprocessingPipeline(ABC):

    name: str
    description:str

    def __init__(self, grid: AutoloaderGrid):
        self.grid = grid
        self.directory = grid.directory

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def list_incomplete_processes(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def update_processes(self):
        to_update = []
        for instance in self.incomplete_processes:
            is_updated, instance = self.check_for_update(instance)
            to_update.append(instance)

    @abstractmethod
    def check_for_update(self, instance):
        pass
    

class SmartScopePreprocessingCmdKwargs(BaseModel):
    n_processes:int = 1
    frames_directory:Union[Path,None] = None

    @validator('frames_directory')
    def is_frame_directory_empty(cls,v):
        logger.debug(f'{v}, {type(v)}')
        if v == '' or v == Path('.'):
            return None
        return v

class PreprocessingPipelineCmd(BaseModel):
    pipeline:str
    cache_id:str = Field(default_factory=generate_unique_id)
    process_pid: Optional[int]
    kwargs: Any

    def is_running(self):
        if self.process_pid is None:
            return False
        try:
            process = psutil.Process(self.process_pid)
            if process.is_running():
                return True
            else:
                return False
        except psutil.NoSuchProcess:
            return False

    def stop(self, grid:AutoloaderGrid):
        stop_file = Path(grid.directory,'preprocessing.stop')
        stop_file.touch()
        while self.is_running():
            try:
                process = psutil.Process(self.process_pid)
            except psutil.NoSuchProcess:
                break
            logger.debug(f'Will check again if process as been killed. This may take a while for all actions to complete.')
            time.sleep(2)
        logger.info('Preprocessing has been killed gracefully.')
    
    def start(self, grid:AutoloaderGrid):
        proc = sub.call(shlex.split(f'/opt/smartscope/Smartscope/bin/smartscope.sh highmag_processing {grid.grid_id}'))
        time.sleep(3)

# class NonBlockingJoinableQueue(multiprocessing.JoinableQueue):

#     def check_join(self, timeout=3):
#         '''Blocks until all items in the Queue have been gotten and processed.

#         The count of unfinished tasks goes up whenever an item is added to the
#         queue. The count goes down whenever a consumer thread calls task_done()
#         to indicate the item was retrieved and all work on it is complete.

#         When the count of unfinished tasks drops to zero, join() unblocks.
#         '''
#         with self.all_tasks_done:
#             while self.unfinished_tasks:
#                 self.all_tasks_done.wait(timeout=timeout)

        

class SmartscopePreprocessingPipeline(PreprocessingPipeline):

    verbose_name = 'SmartScope Preprocessing Pipeline'
    name = 'smartscopePipeline'
    description = 'Default CPU-based Processing pipeline using IMOD alignframe and CTFFIND4.'
    to_process_queue = multiprocessing.JoinableQueue()
    processed_queue = multiprocessing.Queue()
    child_process = []
    to_update = []
    incomplete_processes = []
    cmdkwargs_handler = SmartScopePreprocessingCmdKwargs

    def __init__(self, grid: AutoloaderGrid, cmd_data:Dict):
        super().__init__(grid=grid)
        self.microscope = self.grid.session_id.microscope_id
        self.detector = self.grid.session_id.detector_id
        self.cmd_data = self.cmdkwargs_handler.parse_obj(cmd_data)

        self.frames_directory = [Path(self.detector.frames_directory)]
        if self.cmd_data.frames_directory is not None:
            self.frames_directory.append(self.cmd_data.frames_directory)

    def clear_queue(self):
        while True:
            try:
                self.to_process_queue.get_nowait()
                self.to_process_queue.task_done()
            except multiprocessing.queues.Empty:
                break
        # self.to_process_queue.join()
    
    @classmethod
    def form(cls,data:Union[Mapping,None]=None):
        return SmartScopePreprocessingPipelineForm(data=data)
    
    @classmethod
    def pipeline_data(cls,data:Dict):
        return PreprocessingPipelineCmd(pipeline=cls.name,kwargs=cls.cmdkwargs_handler.parse_obj(data)) 
    
    def is_stop_file(self):
        stopfile = Path('preprocessing.stop')
        if stopfile.is_file():
            stopfile.unlink()
            return True
        return False


    def start(self):
        os.chdir(self.grid.directory)
        session = self.grid.session_id
        for n in range(int(self.cmd_data.n_processes)):
            proc = multiprocessing.Process(target=processing_worker_wrapper, args=(
                session.directory, self.to_process_queue,), kwargs={'output_queue': self.processed_queue})
            proc.start()
            self.child_process.append(proc)
        self.list_incomplete_processes()
        while not self.is_stop_file():
            self.queue_incomplete_processes()
            self.to_process_queue.join()
            # while not self.to_process_queue.check_join(timeout=3):
            #     if not self.is_stop_file():
            #         continue
            #     self.clear_queue()
            self.check_for_update()
            self.update_processes()
            self.list_incomplete_processes()
            self.grid.refresh_from_db()
            if self.grid.status == 'complete' and len(self.incomplete_processes) == 0:
                return
        

    def list_incomplete_processes(self):
        self.incomplete_processes = list(self.grid.highmagmodel_set.filter(status='acquired').order_by('completion_time')[:5*self.cmd_data.n_processes])

    def queue_incomplete_processes(self):
        from_average = partial(process_hm_from_average, scope_path_directory=self.microscope.scope_path,
                               spherical_abberation=self.microscope.spherical_abberation)
        from_frames = partial(process_hm_from_frames, frames_directories=self.frames_directory,
                              spherical_abberation=self.microscope.spherical_abberation)
        for obj in self.incomplete_processes:
            if obj.frames is None or self.detector.detector_model not in ['K2', 'K3'] or self.grid.params_id.force_process_from_average:
                self.to_process_queue.put([from_average, [], dict(raw=obj.raw, name=obj.name)])
            else:
                self.to_process_queue.put([from_frames, [], dict(name=obj.name, frames_file_name=obj.frames)])

    def stop(self):
        for proc in self.child_process:
            self.to_process_queue.put('exit')
            proc.join()
        logger.debug('Process joined')

    def check_for_update(self):
        while self.processed_queue.qsize() > 0:
            movie = self.processed_queue.get()
            if not movie.check_metadata():
                continue
            logger.debug(f'Updating {movie.name}')
            try:
                data = get_CTFFIN4_data(movie.ctf)
            except Exception as err:
                logger.exception(err)
                logger.info(f'An error occured while getting CTF data from {movie.name}. Will try again on the next cycle.')
                continue
            data['status'] = 'completed'
            movie.read_data()
            data['shape_x'] = movie.shape_x
            data['shape_y'] = movie.shape_y
            data['pixel_size'] = movie.pixel_size
            logger.debug(f'Updating {movie.name} with Data: {data}')
            instance = [obj for obj in self.incomplete_processes if obj.name == movie.name][0]
            parent = instance.hole_id
            self.to_update += [update_fields(instance, data), update_fields(parent, dict(status='completed'))]

    def update_processes(self):
        logger.info(f'Updating {len(self.to_update)} items in the database')
        if len(self.to_update) == 0:
            sleep_time = 10
            logger.info(f'No items to update, waiting {sleep_time} seconds before checking again.')
            return time.sleep(sleep_time)
        with transaction.atomic():
            for obj in self.to_update:
                print(obj.shape_x)
                obj.save()
            # [obj.save() for obj in self.to_update]
        websocket_update(self.to_update, self.grid.grid_id)
        self.to_update = []

class SmartScopePreprocessingPipelineForm(forms.Form):
    n_processes = forms.IntegerField(initial=1, min_value=1, max_value=4, help_text='Number of parallel processes to use for preprocessing.')
    frames_directory = forms.CharField(help_text='Locations to look for the frames file other. Will look in the default smartscope/movies location by default.')

    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.required = False

PREPROCESSING_PIPELINE_FACTORY = dict(smartscopePipeline=SmartscopePreprocessingPipeline)

def load_preprocessing_pipeline(file:Path):
    if file.exists():
        return PreprocessingPipelineCmd.parse_file(file)
    logger.info(f'Preprocessing file {file} does not exist. Loading default pipeline.')
    for default in DEFAULT_PREPROCESSING_PIPELINE:
        if default.exists():
            return PreprocessingPipelineCmd.parse_file(default)
    logger.info(f'Default preprocessing pipeline not found.')
    return None 
    

def highmag_processing(grid_id: str, *args, **kwargs) -> None:
    try:
        grid = AutoloaderGrid.objects.get(grid_id=grid_id)
        logging.getLogger('Smartscope').handlers.pop()
        logger.debug(f'Log handlers:{logger.handlers}')
        add_log_handlers(directory=grid.session_id.directory, name='proc.out')
        logger.debug(f'Log handlers:{logger.handlers}')
        preprocess_file = Path(grid.directory,'preprocessing.json')
        cmd_data = load_preprocessing_pipeline(preprocess_file)
        if cmd_data is None:
            logger.info('Trying to load preprocessing parameters from command line arguments.')
            cmd_data = PreprocessingPipelineCmd.parse_obj(**kwargs)
        if cmd_data.is_running():
            logger.info(f'Processings with PID:{cmd_data.process_pid} seem to already be running, please kill the other one before continuing.')
            return
        cmd_data.process_pid=os.getpid()
        preprocess_file.write_text(cmd_data.json())
        pipeline = PREPROCESSING_PIPELINE_FACTORY[cmd_data.pipeline](grid, cmd_data)
        pipeline.start()

    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt as e:
        logger.exception(e)
    finally:
        logger.debug('Wrapping up')
        pipeline.stop()
