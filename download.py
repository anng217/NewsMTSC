"""
Download a specific version of a finetuned model and place it in pretrained_models.
"""
import argparse
import os
import string
from contextlib import suppress

import torch

from fxlogger import get_logger


class Download:
    MODEL_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pretrained_models", "state_dicts")

    def __init__(self, own_model_name, version='default', force=False, list_versions=False):
        from models.FXBaseModel import model_includes_pretrained
        from train import OWN_MODELNAME2CLASS
        logger = get_logger()
        own_model_name = own_model_name
        if version == 'default':
            version = None
        try:
            model_cls = OWN_MODELNAME2CLASS[own_model_name]
        except KeyError:
            logger.error(f'Model "{own_model_name}" is unknown.')
            exit(2)
        if not model_includes_pretrained(model_cls):
            logger.error(f'Model "{own_model_name}" does not ship any pretrained models for download.')
            exit(2)
        if list_versions:
            self.list_versions(model_cls, own_model_name)
        else:
            self.download(model_cls, version, force)

    @staticmethod
    def list_versions(model_cls, own_model_name=''):
        default = model_cls.get_pretrained_default_version()
        versions = model_cls.get_pretrained_versions()
        if own_model_name:
            own_model_name = f' "{own_model_name}"'
        print(f'Model{own_model_name} provides following pretrained versions:')
        for version, source in versions.items():
            default_str = ''
            if version == default:
                default_str = ' (default)'
            print(f'"{version}"{default_str}: {source}')

    @classmethod
    def download(cls, model_cls, version=None, force=False):
        source = model_cls.get_pretrained_source(version)
        path = cls.model_path(model_cls, version)
        if not force and os.path.isfile(path):
            print('Model file already exists. Use --force to overwrite.')
            exit(2)
        print(f'Downloading to {path}:')
        torch.hub.download_url_to_file(source, path)

    @staticmethod
    def model_filename(model_cls, version=None):
        version = version or model_cls.get_pretrained_default_version()
        source_filename = os.path.basename(model_cls.get_pretrained_source(version))
        name = f'{source_filename}_{version}'
        allowed = set(f'.-_ {string.ascii_letters}{string.digits}')
        filename = ''.join(char for char in name if char in allowed)
        return filename.replace('.', '-').replace(' ', '_')

    @classmethod
    def model_path(cls, model_cls, version=None):
        return os.path.join(cls.MODEL_DIRECTORY, cls.model_filename(model_cls, version))

    @staticmethod
    def argument_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--own_model_name",
            default="grutsc",
            type=str
        )
        parser.add_argument(
            "--version",
            default=None,
            type=str,
            help="version of the model to download, use --force to overwrite a version which was already downloaded"
        )
        parser.add_argument(
            "--force",
            action='store_true',
            help="force the download of a model and overwrite potential previous versions"
        )
        parser.add_argument(
            "--list_versions",
            action='store_true',
            help="List all pretrained model versions which a model provides"
        )
        return parser

    @classmethod
    def run_from_cmd(cls):
        args = vars(cls.argument_parser().parse_args())
        return cls(**args)

    @classmethod
    def run_defaults(cls):
        args = vars(cls.argument_parser().parse_args([]))
        return cls(**args)


if __name__ == "__main__":
    Download.run_from_cmd()