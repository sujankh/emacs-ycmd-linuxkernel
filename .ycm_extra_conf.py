# This file is NOT licensed under the GPLv3, which is the license for the rest
# of YouCompleteMe.
#
# Here's the license text for this file:
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

# This file has been copied from https://github.com/Valloric/ycmd/blob/master/.ycm_extra_conf.py
# and modified to fit my use case of Linux Kernel x86 code navigation
# If a header or its corresponding source file is not found, instead of returning
# empty flags, this module will return some basic flags and this makes navigation in those
# header files possible. Otherwise YCMD used to ignore parsing those files
# NOTE: The flags returned might not be applicable for all header files and thus prevent
# navigation in those files.

from distutils.sysconfig import get_python_inc
import platform
import os
import subprocess
import ycm_core

DIR_OF_THIS_SCRIPT = os.path.abspath( os.path.dirname( __file__ ) )
DIR_OF_THIRD_PARTY = os.path.join( DIR_OF_THIS_SCRIPT, 'third_party' )
SOURCE_EXTENSIONS = [ '.cpp', '.cxx', '.cc', '.c', '.m', '.mm' ]


# (skhadka)
# These flags are obtained from a random entry in linux kernel's compile_commands.json
# Modified the entry to remove the file name references. This might need tweaking if ycmd
# does not navigate well.
# Current Issues with these flags
# The flags do not include paths for non-x86 specific architecture preventing navigation of
# files for example in arch/arm/lib/bitops.h
# However this seems to be good enough for x86 and core files like kernel/fork.c, kernel/sched.h etc

flags = [
  "gcc",
  "-c",
  "-nostdinc",
  "-isystem",
  "/usr/lib/gcc/x86_64-linux-gnu/4.8/include",
  "-I./arch/x86/include",
  "-I./arch/x86/include/generated/uapi",
  "-I./arch/x86/include/generated",
  "-I./include",
  "-I./arch/x86/include/uapi",
  "-I./include/uapi",
  "-I./include/generated/uapi",
  "-include",
  "./include/linux/kconfig.h",
  "-D__KERNEL__",
  "-Wall",
  "-Wundef",
  "-Wstrict-prototypes",
  "-Wno-trigraphs",
  "-fno-strict-aliasing",
  "-fno-common",
  "-Werror-implicit-function-declaration",
  "-Wno-format-security",
  "-std=gnu89",
  "-mno-sse",
  "-mno-mmx",
  "-mno-sse2",
  "-mno-3dnow",
  "-mno-avx",
  "-m64",
  "-falign-jumps=1",
  "-falign-loops=1",
  "-mno-80387",
  "-mno-fp-ret-in-387",
  "-mpreferred-stack-boundary=3",
  "-mtune=generic",
  "-mno-red-zone",
  "-mcmodel=kernel",
  "-funit-at-a-time",
  "-maccumulate-outgoing-args",
  "-DCONFIG_AS_CFI=1",
  "-DCONFIG_AS_CFI_SIGNAL_FRAME=1",
  "-DCONFIG_AS_CFI_SECTIONS=1",
  "-DCONFIG_AS_FXSAVEQ=1",
  "-DCONFIG_AS_SSSE3=1",
  "-DCONFIG_AS_CRC32=1",
  "-DCONFIG_AS_AVX=1",
  "-DCONFIG_AS_AVX2=1",
  "-DCONFIG_AS_SHA1_NI=1",
  "-DCONFIG_AS_SHA256_NI=1",
  "-pipe",
  "-Wno-sign-compare",
  "-fno-asynchronous-unwind-tables",
  "-fno-delete-null-pointer-checks",
  "-Wno-maybe-uninitialized",
  "-O2",
  "--param=allow-store-data-races=0",
  "-Wframe-larger-than=2048",
  "-fno-stack-protector",
  "-Wno-unused-but-set-variable",
  "-fno-omit-frame-pointer",
  "-fno-optimize-sibling-calls",
  "-fno-var-tracking-assignments",
  "-Wdeclaration-after-statement",
  "-Wno-pointer-sign",
  "-fno-strict-overflow",
  "-fconserve-stack",
  "-Werror=implicit-int",
  "-Werror=strict-prototypes",
  "-DCC_HAVE_ASM_GOTO",
  "-Os"
]


# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# (skhadka)
# For Linux Kernel, the compile_commands.json file was generated using Bear
# The compile_commands.json file is expected to be in the same directory
# Generated compile_commands.json using Bear (https://github.com/rizsotto/Bear)
database = ycm_core.CompilationDatabase(DIR_OF_THIS_SCRIPT)


def IsHeaderFile( filename ):
  extension = os.path.splitext( filename )[ 1 ]
  return extension in [ '.h', '.hxx', '.hpp', '.hh' ]


def FindCorrespondingSourceFile( filename ):
  if IsHeaderFile( filename ):
    basename = os.path.splitext( filename )[ 0 ]
    for extension in SOURCE_EXTENSIONS:
      replacement_file = basename + extension
      if os.path.exists( replacement_file ):
        return replacement_file
  return filename


# (skhadka) This function is called by ycmd ycmd/completers/cpp/flags.Flags and _CallExtraConfFlagsForFile
# Expects us to return Flags
# More details in https://github.com/Valloric/ycmd#ycm_extra_confpy-specification

def Settings( **kwargs ):
  language = kwargs[ 'language' ]

  if language == 'cfamily':
    # If the file is a header, try to find the corresponding source file and
    # retrieve its flags from the compilation database if using one. This is
    # necessary since compilation databases don't have entries for header files.
    # In addition, use this source file as the translation unit. This makes it
    # possible to jump from a declaration in the header file to its definition
    # in the corresponding source file.
    filename = FindCorrespondingSourceFile( kwargs[ 'filename' ] )
    compilation_info = database.GetCompilationInfoForFile( filename )

    # (skhadka)
    # If the header does not have an entry in the database or does not have a
    # corresponding source file, just return the flags above
    # This will make sure that some basic navigation will be enabled
    # Else, ycmd will error out with some AST parsing error
    if not compilation_info.compiler_flags_:
      print(filename + " was not in the compilation db; Returning default flags")
      return {
        'flags': flags,
        'include_paths_relative_to_dir': DIR_OF_THIS_SCRIPT,
        'override_filename': filename
      }

    # Bear in mind that compilation_info.compiler_flags_ does NOT return a
    # python list, but a "list-like" StringVec object.
    final_flags = list( compilation_info.compiler_flags_ )
    return {
      'flags': final_flags,
      'include_paths_relative_to_dir': compilation_info.compiler_working_dir_,
      'override_filename': filename
    }

  return {}
