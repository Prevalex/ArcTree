#?
# Import the os module, for the os.walk function
import os
import re
import sys
from alx import dbg, pause
import subprocess
import datetime
import argparse

max_ret_code = 0
saved_n2d_rc = 0

vertical_1 = '\u2016' # '‖'
vertical_2 = '\u2551' # '║'
slash_1 = '\u2044' # '⁄'
slash_2 = '\u2215' # '∕'
backslash_1 = '\uFF3C' # '＼'  U+FF3C: FULLWIDTH REVERSE SOLIDUS
backslash_2 = '\u29F5' # '⧵'   U+29F5: REVERSE SOLIDUS OPERATOR
backslash_3 = '\u29F9' # '⧹'



fs_limit: int = 4294963200  #file size limit for Fat 32 minus 4K: int(0b11111111111111111111000000000000) = 4294963200

err_invalid_arg = 101  # invalid arguments
err_no_path = 102  # path not found
err_no_dir = 103  # path is not a folder
err_no_exe = 104  # archiver exe file not found in the OS Path
err_not_run = 105  # archiver has been never run

was_running_marker = False

ignore_names_list = ['desktop.ini', 'thumbs.db']

zip_dict = {
    -3: '*.*',
    -2: 8,
    -1: 'zip',
    0: ['PkZipC', '-add=update', f'-span={fs_limit}', '-max', '-deflate64', '-silent=progress,banner', '-UTF8', '-path=current'],
    2: "Ambiguous option or command specified.",
    3: "Ambiguous sub-option specified.",
    4: "Unknown or illegal option.",
    5: "Unknown or illegal sub-option.",
    6: "No .ZIP file specified.",
    7: "Can't create file",
    8: "Nothing to do!",
    9: "No file(s) were processed.",
    10: "No files specified for deletion.",
    11: "Disk full.",
    12: "Can't find file.",
    13: "Can't open .ZIP file.",
    14: "Can't create archive.",
    15: "Renaming temporary .ZIP file.",
    16: "Can't open for write access.",
    17: "Error encrypting file data.",
    18: "Can't open list file.",
    19: "Aborted file extract.",
    20: "Aborted file compression.",
    21: "Can't modify a spanned or split .ZIP file",
    22: "Cannot format removable media.",
    23: "Suboption is too long",
    26: "Device not ready.",
    27: "2.04g compatibility cannot be used with the option",
    28: "Share violation, file is in use by another process",
    29: "Missing sub-option",
    34: "Invalid archive format",
    58: "Invalid archive - method not supported.",
    65: "Could not encode archive file.",
    71: "Can't open PKCS#7 file.",
    72: "Smartcrypt wanted user input, but silent=input or silent=all was specified",
    73: "Warning configured as an error",
    75: "Incorrect passphrase or certificate not found, unable to open archive: <archive name>",
    76: "Cannot open alternate config file.",
    77: "Archive can only support one file inside!",
    78: "Unable to FTP archive file.",
    79: "Unable to E-mail archive file.",
    80: "Unable to run anti-virus",
    81: "Possible virus detected",
    82: "Too many recipients, recipient count limited to 3275 certificates",
    83: "Specified SFX cannot extract archive created with the option.",
    84: "Fatal policy error, contact your system administrator",
    85: "Unable to encrypt, no certificates passed -strict check",
    86: "Archive is not signed by a specified verification certificate",
    87: "Certificate not found.",
    88: "Multiple certificates found.",
    89: "Policy requires the ZIP archive to be encrypted",
    90: "Policy requires the ZIP archive and/or files to be signed",
    91: "Policy prohibits creation of non-ZIP archives",
    92: "Timeout error on file.",
    93: "Timestamp failed",
    94: "Can't modify a timestamped .ZIP.",
    98: "Encryption verification failed",
    99: "AE-x encryption cannot be used with the option -[name]",
    100: "Insufficient memory",
    150: "Error reading .ZIP file.",
    155: "Too many files in archive",
    156: "File is now too big for valid zip data.",
    157: "This archive requires a product compliant with ZIP APPNOTE version XX.X",
    158: "Errors encountered reading archive",
    171: "Unable to encrypt for the Smartkey",
    172: "Unable to update Smartkey encrypted archive.",
    173: "Unable to create Smartkey",
    174: "Unable to modify Smartkey",
    175: "Unable to delete Smartkey",
    176: "Policy conflict",
    200: "FIPS 140 mode is enabled, but archive is not encrypted with a FIPS-approved algorithm",
    201: "FIPS 140 mode is enabled, but encryption requested is not a FIPS-approved algorithm",
    202: "FIPS 140 mode is enabled, but signature hash requested is not a FIPS-approved algorithm",
    203: "FIPS 140 mode failed to initialize",
    204: "The specified certificate does not meet the minimum requirements for signing when FIPS mode is enabled",
    205: "The specified certificate does not meet the minimum requirements for encrypting when FIPS mode is enabled.",
    249: "Unable to start agent: [text]",
    254: "Your evaluation period for Smartcrypt has expired. Please register to continue using this product.",
    255: "User pressed ctrl-c or control-break."
}

rar_dict = {
    -3: '*.*',
    -2: 10,
    -1: 'rar',
    #0:['Rar','u', '-m5', '-ma5','-msrar;zip;jpg;mov'],
    #0: ['Rar', 'u', '-m5', '-ma5'],
    0: ['Rar', 'u', '-m5', f'-v{fs_limit}b'],
    1: "Non fatal error(s) occurred.",
    2: "A fatal error occurred.",
    3: "Invalid checksum. Data is damaged.",
    4: "Attempt to modify an archive locked by 'k' command.",
    5: "Write error.",
    6: "File open error.",
    7: "Wrong command line option.",
    8: "Not enough memory.",
    9: "File create error",
    10: "No files matching the specified mask and options were found.",
    11: "Wrong password.",
    12: "Read error.",
    255: "User stopped the process."
}

z7_dict = {
    -3: '*',
    -2: -1,
    -1: '7z',
    0: ['7z', 'u', f'-v{fs_limit}b', '-t7z', '-r-', '-mx9', '-x!*\\', '-scsUTF-8'],
    1: 'Warning (Non fatal error(s)). For example, one or more files were locked by some other application, '
       'so they were not compressed.',
    2: "Fatal error",
    7: "Command line error",
    8: "Not enough memory for operation",
    255: "User stopped the process"
}


def is_dir_empty(file_list):
    if len(file_list) < 1:
        return True
    for file_name in file_list:
        if all(file_name.lower() != ignore_name for ignore_name in ignore_names_list):
            return False
    return True


def get_archiver_exe_path(progname):
    execfile = os.path.join(os.getcwd(), progname + '.exe')
    if os.path.exists(execfile):
        if os.path.isfile(execfile):
            return execfile

    for path in os.environ["PATH"].split(os.pathsep):
        if not path == "":
            execfile = os.path.join(path, progname + '.exe')
            if os.path.exists(execfile):
                if os.path.isfile(execfile):
                    return execfile
    else:
        print()
        print(f'{sys.argv[0]}: Error:Archiver {progname}.exe not found in the os path')
        exit(err_no_exe)


def arch_err_msg(arch_dict, err_num):
    if err_num in arch_dict:
        return f'{arch_dict[0][0]}: "{arch_dict[err_num].strip()}"'
    else:
        return f'{arch_dict[0][0]}: ErrorCode {err_num}: Unknown Error'


def is_root_dir(dirpath):
    return re.search(r"^[a-zA-Z]:\\$", dirpath)


def get_drive_sign(dir_path):
    return dir_path[0:1].upper() + "$"


def get_is_empty_sign(dir_path, flist):
    if len(flist) == 0:
        return "[:._]"

    if is_dir_empty(flist):
        return "[:..]"

    _dir = os.path.basename(dir_path).lower()
    if (_dir == '.tmp.drivedownload') or (_dir == '.tmp.driveupload'):
        return "[:..]"

    return ""


def get_time_stamp(flag):
    """
    Generates a time stamp in two formats: for inclusion in the file name and for inclusion in the log entry
    takes parameters (str):
        "f" - generate for filename
        other - generate for the log
    """
    stamp = str(datetime.datetime.now())
    if flag.lower().strip() == 'f':
        stamp = stamp[0:10] + "_" + stamp[11:13] + "-" + stamp[14:16] + "-" + stamp[17:19]
    else:
        stamp = stamp[0:10] + " " + stamp[11:13] + ":" + stamp[14:16] + ":" + stamp[17:19]
    return stamp

def delimit_path(path_str:str, slash_flag):
    _path_list =  path_str.split('\\')
    if slash_flag:
        return backslash_1.join(_path_list)
        #return path_part + slash_z1
    else:
        return "[" + "][".join(_path_list) + "]"
        #return "[" + path_part + "]"

def write_to_log(logfile_handle, logstring):
    print(logstring)

    if logstring[0:5] == "[:->]":
        print()

    logfile_handle.write(logstring + '\n')
    logfile_handle.flush()


def get_abs_path(dir_path):
    if not os.path.exists(dir_path):
        print()
        print(f'{sys.argv[0]}: Error: Folder "{dir_path}" not found')
        exit(err_no_path)
    elif not os.path.isdir(dir_path):
        print()
        print(f'{sys.argv[0]}: Error: "{dir_path}" is not a folder')
        exit(err_no_dir)
    else:
        return os.path.abspath(dir_path)


def get_arcfile_status_msg(dir_path, filename_without_ext, archiver_ret_code):
    filename_with_path = f'{dir_path}\\{filename_without_ext}.{curr_arc_dict[-1]}'
    if not os.path.exists(filename_with_path):
        return f'Archive File is Not Created: "{filename_with_path}"'
    elif not os.path.isdir(dir_path):
        return f'Archive File is Not Created: "{filename_with_path}"'
    elif archiver_ret_code == 0:
        return f'Archive File is: "{filename_with_path}"'
    else:
        return f'Archive File Exists: "{filename_with_path}"'


the_parser = argparse.ArgumentParser(description='Compress the folder tree per folder')
the_parser.add_argument('sourcePath',
                        metavar='sourcePath',
                        type=str,
                        help='Path to the top folder of the source tree')

the_parser.add_argument('destPath',
                        metavar='destPath',
                        type=str,
                        help='Path to the destination folder where to save the archive')

the_parser.add_argument('-a',
                        type=str,
                        choices=['zip', 'rar', '7z'],
                        help='An optional parameter to specify the archiver.'
                             f' Use zip for {zip_dict[0][0]}.exe,'
                             f' or rar for {rar_dict[0][0]}.exe,'
                             f' or 7z for {z7_dict[0][0]}.exe. Default is rar.')

the_parser.add_argument('-s','--slash',
                        action='store_true',
                        help='Use slash in archive file name tas a path delimiter')

if __name__ == '__main__': # don't need but let it be

    args = the_parser.parse_args()  # args is a Namespace type/class
    dbg(args)

    curr_arc_dict = rar_dict

    if args.a:
        if args.a == 'rar':
            curr_arc_dict = rar_dict
        elif args.a == '7z':
            curr_arc_dict = z7_dict
        elif args.a == 'zip':
            curr_arc_dict = z7_dict

    start_dir = get_abs_path(args.sourcePath)
    argv_store_dir = get_abs_path(args.destPath)
    get_archiver_exe_path(curr_arc_dict[0][0])

    if len(argv_store_dir) == 3 and argv_store_dir[2] == "\\":
        store_dir = argv_store_dir[:-1]
    else:
        store_dir = argv_store_dir

    parent_dir = get_abs_path(start_dir + "\\..")
    start_dir_path_list = start_dir.split("\\")

    if is_root_dir(start_dir):
        start_dir_name = get_drive_sign(start_dir)
        #preName = "[" + start_dir_name + "]"
        preName = delimit_path(start_dir_name, args.slash) # 20.12.24
    else:
        start_dir_name = start_dir_path_list[len(start_dir_path_list) - 1]
        preName = ""

    log_name = f"{start_dir_name}_{get_time_stamp('f')}_{curr_arc_dict[-1].capitalize()}Tree.Log"

    log_name_with_path = store_dir + '\\' + log_name

    log_file_handle = open(log_name_with_path, "w+", encoding='utf-8')

    mLine = (f":.. = {curr_arc_dict[0][0]} not launched: Folder ignored (.tmp.drivedownload, .tmp.driveupload or contains "
             f"only \"desktop.ini\" and/or \"thumbs.db\" files")

    sLine = "_" * len(mLine)

    write_to_log(log_file_handle, sLine)
    write_to_log(log_file_handle, "")
    write_to_log(log_file_handle, f'{sys.argv[0]}:')
    write_to_log(log_file_handle, "")
    write_to_log(log_file_handle, f' Top Source folder: {start_dir}')
    write_to_log(log_file_handle, f' Arc Store  folder: {argv_store_dir}')
    write_to_log(log_file_handle, f' Log File name:     {log_name_with_path}')

    write_to_log(log_file_handle, sLine)

    write_to_log(log_file_handle, '')
    write_to_log(log_file_handle, 'Log Signs in square brackets:')
    write_to_log(log_file_handle, '')

    write_to_log(log_file_handle, f":>> = Script Started")
    write_to_log(log_file_handle, f":<< = Script Finished Successfully")
    write_to_log(log_file_handle, f"!<< = Script Finished Successfully, but the archiver reported errors or warnings")
    write_to_log(log_file_handle, f":-> = {curr_arc_dict[0][0]} Started")
    write_to_log(log_file_handle, f":=0 = {curr_arc_dict[0][0]} Finished with ErrorCode = 0")
    if curr_arc_dict[-2] > 0:
        write_to_log(log_file_handle, f":={curr_arc_dict[-2]} = {curr_arc_dict[0][0]} Archiver Returned 'Nothing to do' "
                                      f"ErrorCode={curr_arc_dict[-2]}")
    write_to_log(log_file_handle, f":!E = {curr_arc_dict[0][0]} Finished with ErrorCode = E (Where E = number from "
                                  f"1 to 255)")
    write_to_log(log_file_handle, f":._ = {curr_arc_dict[0][0]} not launched: Folder Empty")
    # mline is difened above
    write_to_log(log_file_handle, mLine)

    write_to_log(log_file_handle, sLine)

    write_to_log(log_file_handle, "")

    #log_string = f"[:>>] {get_time_stamp('l')} Started: {sys.argv[0]} {sys.argv[1]} {sys.argv[2]}\n"
    log_string = f"[:>>] {get_time_stamp('l')} Started: {' '.join(sys.argv)}\n"
    write_to_log(log_file_handle, log_string)

    exe_file = get_archiver_exe_path(curr_arc_dict[0][0])

    for dirName, subdirList, fileList in os.walk(start_dir):

        full_path = os.path.abspath(dirName)
        rel_path = os.path.relpath(dirName, start=parent_dir)

        full_path_list = full_path.split("\\")
        rel_path_list = rel_path.split("\\")

        empty_flag = get_is_empty_sign(full_path, fileList)

        if empty_flag != "":
            log_string = f"{empty_flag} {get_time_stamp('l')} {full_path}\n"
            write_to_log(log_file_handle, log_string)
        else:

            if is_root_dir(full_path):
                arc_name = preName
            else:
                #arc_name = preName + "[" + "][".join(rel_path_list) + "]"
                arc_name = preName + delimit_path(rel_path, args.slash)

            storPath = f'{store_dir}\\{arc_name}.{curr_arc_dict[-1]}'

            if is_root_dir(full_path):
                what2zip = f'{rel_path}\\{curr_arc_dict[-3]}'
            else:
                what2zip = f'.\\{rel_path}\\{curr_arc_dict[-3]}'

            os.chdir(parent_dir)  # ! Here!

            cmd_list = curr_arc_dict[0].copy()
            cmd_list.extend([storPath, what2zip])

            cmdline = " ".join(cmd_list)

            exe_list = cmd_list.copy()
            exe_list[0] = exe_file

            log_string = f"[:->] {get_time_stamp('l')} {os.getcwd()}>{cmdline}"
            write_to_log(log_file_handle, log_string)
            ###########################################################################################################
            result = subprocess.run(exe_list, shell=False)
            if result:
                curr_ret_code = result.returncode
                was_running_marker = True
            else:
                curr_ret_code = -1
            ###########################################################################################################

            file_existence_status_str = get_arcfile_status_msg(store_dir, arc_name, curr_ret_code)

            if curr_ret_code == 0:
                log_string = f"[:={curr_ret_code}] {get_time_stamp('l')} {file_existence_status_str}\n"
            elif curr_ret_code == curr_arc_dict[-2]:
                log_string = f"[:={curr_ret_code}] {get_time_stamp('l')} {arch_err_msg(curr_arc_dict, curr_ret_code)}, " \
                             f"{file_existence_status_str}\n"
                saved_n2d_rc = curr_arc_dict[-2]
            else:
                log_string = f"[:!{curr_ret_code}] {get_time_stamp('l')} {arch_err_msg(curr_arc_dict, curr_ret_code)}, " \
                             f"{file_existence_status_str}\n"
                if curr_ret_code > max_ret_code:
                    max_ret_code = curr_ret_code
            write_to_log(log_file_handle, log_string)

    if was_running_marker:
        if max_ret_code == 0:
            if saved_n2d_rc == curr_arc_dict[-2]:
                log_string = f"[!<<] {get_time_stamp('l')} Finished with \"Nothing to do\" warnings. Details:" \
                             f" {log_name_with_path}"
            else:
                log_string = f"[:<<] {get_time_stamp('l')} Successfully Finished [RC={max_ret_code}]. Details: " \
                             f"{log_name_with_path}"
        else:
            log_string = f"[!<<] {get_time_stamp('l')} Finished with highest error code: [{max_ret_code}]. Details: " \
                         f"{log_name_with_path}"
    else:
        log_string = f"[:<<] {get_time_stamp('l')} The archiver has never been launched. Details: {log_name_with_path}"
        max_ret_code = err_not_run

    write_to_log(log_file_handle, log_string)

    log_file_handle.close()
    exit(max_ret_code)
