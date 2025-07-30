import filecmp
import logging
import pycarta as pc
import sevenbridges as sbg
import shutil
import os
from time import sleep


# logging.getLogger("pycarta").setLevel(logging.DEBUG)


class dircmp(filecmp.dircmp):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path.
    """
    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison with shallow=False.
        """
        fcomp = filecmp.cmpfiles(self.left,
                                 self.right,
                                 self.common_files,
                                 shallow=False)
        self.same_files, self.diff_files, self.funny_files = fcomp

    def __bool__(self):
        if (self.left_only or self.right_only or self.diff_files or self.funny_files):
            return False
        for subdir in self.common_dirs:
            if not dircmp(os.path.join(self.left, subdir),
                          os.path.join(self.right, subdir)):
                return False
        return True
    

api = sbg.Api(config=sbg.Config(profile='default'))
print("Created API:", api)
project = api.projects.query(name='sandbox-branden')[0]
print("Found project:", project)

# Try to delete a directory
folder = pc.sbg.base.SbgDirectory("delme")
print("Created SbgDirectory:", folder)
folder.upload(project=project, api=api)
sleep(30)
folder.delete()

# # Upload
# folder = pc.sbg.base.SbgDirectory("delme")
# print("Created SbgDirectory:", folder)
# folder.upload(project=project, api=api)
# print("Uploaded SbgDirectory")
# shutil.move("delme", "delme.bkp")
# print("Moved delme to delme.bkp")
# # Download
# folder.download("delme", recurse=True)
# print("Downloaded SbgDirectory")

# try:
#     if not bool(dircmp("delme", "delme.bkp")):
#         raise IOError()
# except:
#     print(f"FAILED: Upload and download of a directory do not match.")
# else:
#     print("SUCCESS: Uploaded and downloaded a directories match.")
# finally:
#     # Cleanup
#     shutil.rmtree("delme")
#     shutil.move("delme.bkp", "delme")
#     print("Cleaned up delme and restored delme.bkp")

# # delme already exists remotely, this should error out
# try:
#     folder.upload(project=project, exists_ok=False, api=api)
# except:
#     print("SUCCESS: errored out when uploading a directory that already exists remotely.")
# else:
#     print("FAILED: Upload of an existing directory should have errored.")

