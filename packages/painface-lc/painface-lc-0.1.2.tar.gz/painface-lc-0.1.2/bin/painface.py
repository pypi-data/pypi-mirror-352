#!python

import sys
import os 
import traceback
import shutil
import argparse
from argparse import RawTextHelpFormatter
from pathlib import Path
sys.path.append(Path(__file__).resolve().parent.parent.__str__()) ## this line is for development

from painfacelib.config import INFO as info
import painfacelib.common as common
from painfacelib.ui import gui, tui
import painfacelib.ml as ml
import painfacelib.ml.estimate as e

logger=common.logger.write 
color= common.Color

@common.measure_time
def command_estimate_video(args):
    payload = {
        'type': 'datasetdir',
        'fau_model_dir': args.fau_model_dir,
        'mgs_model_dir': args.mgs_model_dir,
        'output_dir': args.output_dir,
        'data_path': args.video_path,
        'subject_type':args.subject_type,
        'study_type':args.study_type,
        'interval':args.interval,
        'visualize': args.visualize,
        'gpu':args.gpu,
        'dev':args.dev
    }
    e.estimate_video(payload)

def command_gui(args):
    app = gui.Application()
    app.run()

def command_tui(args):
    common.not_implemented()

### Argparser

def get_args():

    version=info['painface']['version']
    logger("VERSION : {}".format(str(version)))
    config_dir=Path.home().joinpath('.painface').resolve()
    config_dir.mkdir(exist_ok=True, parents=True)
    
    fau_default_dir = config_dir.joinpath('models').joinpath('c57bl6').joinpath('fau').joinpath('default').__str__()
    mgs_default_dir = config_dir.joinpath('models').joinpath('c57bl6').joinpath('pain-mgs').joinpath('default').__str__()

    uid, ts = common.get_uuid(), common.get_timestamp()
    
    ### Argument parsers

    parser=argparse.ArgumentParser(prog="painface",
                                   formatter_class=RawTextHelpFormatter,
                                   description="Painface is general grimace scoring software from animal videos.",
                                   epilog="Written by SK Park (sangkyoon_park@med.unc.edu) ,  Zylka Lab, Department of Cell Biology, University of North Carolina @ Chapel Hill , United States, 2025")
    subparsers=parser.add_subparsers(help="Commands")

    ## estimate video command
    parser_run=subparsers.add_parser('run',help='Estimate video')
    parser_run.add_argument('video_path', help="Video filename to estimate", type=str)
    parser_run.add_argument('--fau-model-dir', help='Fau model directory', default=fau_default_dir , type=str)
    parser_run.add_argument('--mgs-model-dir', help='MGS model directory', default=mgs_default_dir, type=str)
    parser_run.add_argument('-g','--gpu',help="gpu to use", default='0',type=str)
    parser_run.add_argument('-o','--output-dir',help="output directory", required=True,type=str)
    parser_run.add_argument('-s','--subject-type',help="subject type",default='c57bl/6',type=str)
    parser_run.add_argument('-i','--interval',help='interval of evaluation', default=1000,type=int)
    parser_run.add_argument('--study-type',help="study type",default='pain-mgs',type=str)
    parser_run.add_argument('--visualize', help="visualize mode", default=False, action="store_true")
    parser_run.add_argument('--dev', help="debug mode", default=False, action="store_true")
    parser_run.set_defaults(func=command_estimate_video)

    ## gui command
    parser_gui=subparsers.add_parser('gui',help='Run GUI Desktop Application',epilog="Run Painface GUI")
    parser_gui.set_defaults(func=command_gui)
    
    ## gui command
    parser_tui=subparsers.add_parser('tui',help='Run TUI Desktop Application',epilog="Run Painface TUI")
    parser_tui.set_defaults(func=command_tui)

    ## Log related (basic args)
    parser.add_argument('--config-dir',help='Configuration directory',default=str(config_dir))
    parser.add_argument('--log',help='log file',default=str(config_dir.joinpath('log.txt')))
    parser.add_argument('--execution-id',help='execution id',default=uid,type=str)
    parser.add_argument('--no-log-timestamp',help='Remove timestamp in the log', default=False, action="store_true")
    parser.add_argument('--no-verbosity',help='Do not show any logs in the terminal', default=False, action="store_true")
    parser.add_argument('-v','--version', help="Show version", default=False,action="store_true")

    ## if no parameter is furnished, exit with printing help
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args=parser.parse_args()
    if args.version:
        sys.exit(1)

    return args


if __name__ == '__main__':
    args = get_args()
    try:
        common.logger.setTimestamp(True)
        result=args.func(args)
        exit(0)
    except Exception as e:
        common.logger.setVerbosity(True)
        msg=traceback.format_exc()
        logger(msg,color.ERROR)
        exit(-1)
    finally:
        pass
