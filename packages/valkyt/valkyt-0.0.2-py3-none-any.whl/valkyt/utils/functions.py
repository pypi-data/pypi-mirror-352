import jmespath
import shutil

from .directory import Dir
class Funct:

    @staticmethod
    def copy(source: str, destination: str) -> str:
        Dir.create_dir('/'.join(destination.split('/')[:-1]))
        destination: str = shutil.copy2(source=source, dst=destination)

        return destination
        ...
        
    @staticmethod
    def find(datas: list, value: str, key: str, **kwargs) -> dict:
        if not value:
            return datas
        try:
            return jmespath.search(f"[?{key} == `{int(value)}`] | [0]", datas) or \
                jmespath.search(f"[?contains(lower({key}), '{value.lower()}')] | [0]", datas)
        except:
            return jmespath.search(f"[?contains(lower({key}), '{value.lower()}')] | [0]", datas)