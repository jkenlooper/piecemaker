import os

from piecemaker.glue.compat import iteritems


class BaseFormat(object):

    extension = None
    build_per_ratio = False

    def __init__(self, sprite):
        self.sprite = sprite

    def output_dir(self, *args, **kwargs):
        return self.sprite.config["{0}_dir".format(self.format_label)]

    def output_filename(self, ratio=None, *args, **kwargs):
        if self.build_per_ratio:
            if ratio is None:
                raise AttributeError(
                    "Format {0} output_filename requires a ratio.".format(
                        self.__class__
                    )
                )
            ratio_suffix = "@%.1fx" % ratio if int(ratio) != ratio else "@%ix" % ratio
            if ratio_suffix == "@1x":
                ratio_suffix = ""
            return "{0}{1}".format(self.sprite.name, ratio_suffix)
        return self.sprite.name

    def output_path(self, *args, **kwargs):
        return os.path.join(
            self.output_dir(*args, **kwargs),
            "{0}.{1}".format(self.output_filename(*args, **kwargs), self.extension),
        )

    def build(self):
        if self.build_per_ratio:
            for ratio in self.sprite.config["ratios"]:
                self.save(ratio=ratio)
        else:
            self.save()

    def save(self, *args, **kwargs):
        raise NotImplementedError

    def needs_rebuild(self):
        return True

    def validate(self):
        pass

    @property
    def format_label(self):
        from piecemaker.glue.formats import formats

        return dict((v, k) for k, v in iteritems(formats))[self.__class__]

    @classmethod
    def populate_argument_parser(cls, parser):
        pass

    @classmethod
    def apply_parser_contraints(cls, parser, options):
        pass

    def fix_windows_path(self, path):
        if os.name == "nt":
            path = path.replace("\\", "/")
        return path
