import re, sys, os
import importlib


def module_object(self, path: str):
    try:
        path_split = path.split('.')
        class_name = path_split[-1]
        module_name = path_split[-2]
        path_obj = '.'.join(path_split[:-2])
        path_re = re.sub('\.\.', '../', path_obj)
        path_re = re.sub(r'(?<!\.)(\.)(?!\.)', '/', path_re)
        if path_re.startswith('/'):
            path_re = '.' + path_re
    except Exception as e:
        MSG = f"{path} => pipeline path error ==>> "
        raise Exception(MSG + str(e))
    try:
        sys.path.append(path_re)
        module = __import__(module_name)
        class_obj = getattr(module, class_name)
        return class_obj
    except Exception as e:
        MSG = f"Get module False => WorkDir: {self.work_dir} ==> Pipeline: {path} ===>>> "
        raise Exception(MSG + str(e))


def pipeline_sort(item, reverse=True):
    return dict(sorted(item.items(), key=lambda x: x[1], reverse=reverse))


def pipeline_start(self):
    self.pipelines_list = list()
    pipelines_open_spider = self.pipelines
    if pipelines_open_spider:
        pipelines_open_spider = pipeline_sort(pipelines_open_spider)
        for pipeline, level in pipelines_open_spider.items():
            class_obj = module_object(self, pipeline)
            self.class_obj = class_obj()
            open_spider = getattr(self.class_obj, 'open_spider', None)
            if open_spider:
                self.class_obj.open_spider(self)
            setattr(self, class_obj.__name__, self.class_obj)
            self.pipelines_list.append(class_obj.__name__)


def pipeline_process_item(item, self):
    pipelines_list = self.pipelines_list
    if pipelines_list:
        for pipeline in pipelines_list:
            class_obj = getattr(self, pipeline, None)
            process_item = getattr(class_obj, 'process_item', None)
            if process_item:
                item = class_obj.process_item(item, self)
                if not item:
                    break
            else:
                self.loging.warn(f"Pipeline <{pipeline}.process_item> is None")


def pipeline_close(self):
    pipelines_list = self.pipelines_list
    if pipelines_list:
        for pipeline in pipelines_list:
            class_obj = getattr(self, pipeline, None)
            close_spider = getattr(class_obj, 'close_spider', None)
            if close_spider:
                class_obj.close_spider(self)
