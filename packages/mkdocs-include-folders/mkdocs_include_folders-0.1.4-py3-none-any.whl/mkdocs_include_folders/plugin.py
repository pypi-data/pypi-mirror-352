import fnmatch
import re
import os
import mkdocs
import mkdocs.plugins
import mkdocs.structure.files

class IncludeFolders(mkdocs.plugins.BasePlugin):
    """A mkdocs plugin that prioritizes and adds all matching files and folders from the input list."""

    config_scheme = [
        ('priority_path', mkdocs.config.config_options.Type((str, list), default=None))
    ]

    def on_files(self, files, config):
        paths = self.config['priority_path'] or []
        if not isinstance(paths, list):
            paths = [paths]
        out = []
        docfiles = {}
        
        def prioritize_files(path):
            for f in files:
                # normalize path divider changing to linux '/' instead of windows '\'
                f.abs_src_path = os.path.normpath(f.abs_src_path)
                f.abs_dest_path = os.path.normpath(f.abs_dest_path)
                if fnmatch.fnmatchcase(f.src_uri,path):
                    # strip the path name from the files and skip file if an identical name is already added to docfiles
                    index = re.sub(path,"",f.url)
                    if index in docfiles:
                        print(f"- already found {index}, src {docfiles[index]}")
                        continue
                    f.src_uri = re.sub(path,"",f.src_uri)
                    #f.abs_src_path = re.sub(path,"",f.abs_src_path)
                    f.abs_dest_path = re.sub(path,"",f.abs_dest_path)
                    f.dest_uri = re.sub(path,"",f.dest_uri)
                    f.url = index 
                    docfiles[index] = f 
                if fnmatch.fnmatchcase(f.src_uri,"assets/*"):
                    docfiles[f.src_uri] = f
                    #print(f"- adding assets {f.src_uri}")
        
        # Scan through list of prioritized paths
        for p in paths:
            prioritize_files(p)
        
        # Append filtered docfiles to file structure
        for key in docfiles:
            file = docfiles[key]
            out.append(file)
        return mkdocs.structure.files.Files(out)
