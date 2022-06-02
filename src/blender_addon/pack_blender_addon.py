from dataclasses import dataclass
from pathlib import Path
import shutil


def get_addon_version():
    from src.blender_addon.speckly.__init__ import bl_info
    version = bl_info['version']
    return '.'.join([str(num) for num in version])


@dataclass
class PackExternalFiles:
    files_to_pack: dict
    temp_dir: Path = None
    files_kept: dict = None

    def __post_init__(self):
        if self.temp_dir is None:
            raise ValueError(f'A temporal directory is needed')

    def __enter__(self):
        self.files_kept = {}
        self.keep_destination_files_if_any()
        self.place_external_files()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore_original_files_if_any()

    def keep_destination_files_if_any(self):
        self.temp_dir.mkdir()
        for filepath in self.files_to_pack.values():
            if filepath.exists():
                dest_path = self.temp_dir / filepath.name
                shutil.move(str(filepath), str(dest_path))
                self.files_kept[dest_path] = filepath

    def place_external_files(self):
        for path_src, path_dst in self.files_to_pack.items():
            shutil.copy2(str(path_src), str(path_dst))

    def restore_original_files_if_any(self):
        for filepath in self.files_to_pack.values():
            filepath.unlink()
        for path_src, path_dst in self.files_kept.items():
            shutil.move(str(path_src), str(path_dst))
        self.temp_dir.rmdir()


def pack_addon():
    path = Path().resolve()
    external_files_to_pack = {
        path.parent / 'natural_language_processing' / 'speckle_io.py': path / 'speckly' / 'io.py'
    }
    release_path = path / 'releases' / f'speckly_addon_{get_addon_version()}'
    addon_dir = 'speckly'
    temp_dir = path.parent / 'packing_temp_dir'
    with PackExternalFiles(files_to_pack=external_files_to_pack, temp_dir=temp_dir):
        shutil.make_archive(str(release_path), 'zip', str(path), addon_dir)
    print(f'Addon packed in: {release_path}')


if __name__ == '__main__':
    pack_addon()
