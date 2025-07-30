import os
import sys
import glob
import time
import shutil
import subprocess
import psutil
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s:  %(message)s')
from helper import remove_folder, kill_process, unzip_file
from simufact import simufactIns


class SilentInstallation:
    def __init__(self, name):
        self._prod = simufactIns[name]
        self._isRel = os.environ['IS_REL'] == 'True'
        self._isSc = os.environ['MARKEXPR'] == 'sc'
        self._installationRoot = os.path.join('c:'+os.sep, f'{name}_rel' if self._isRel or self._isSc else name)

    def get_latest_build(self, is_rel: bool) -> str:
        shared_path = os.environ["SHARED_REL_PATH"] if is_rel else os.environ["SHARED_PATH"]
        shared_path = os.path.join(shared_path, f'_setup_{self._prod.alias}')
        builds = sorted(
            (f for f in glob.iglob(f'{shared_path}/*') if os.path.isfile(f) and f.endswith('.7z')),
            key=os.path.getmtime, reverse=True)
        for build in builds:
            in_progress_flag = build.replace('.7z', '_in_progress')
            if os.path.isfile(in_progress_flag):
                logging.warning(f'{in_progress_flag} does exist now, check next latest one.')
                continue
            return build
        return ''

    def get_build_rec(self):
        if self._isSc:
            last_build_rec = os.path.join(os.path.expanduser("~"), 'Downloads', f'last_{self._prod.name}_sc.txt')
        elif self._isRel:
            last_build_rec = os.path.join(os.path.expanduser("~"), 'Downloads', f'last_{self._prod.name}_rel.txt')
        else:
            last_build_rec = os.path.join(os.path.expanduser("~"), 'Downloads', f'last_{self._prod.name}_trunk.txt')
        return last_build_rec

    def check_new_build(self, last_build_rec: str):
        if os.environ['SPE_NUM'] == 'none':
            latest_build = self.get_latest_build(self._isSc or self._isRel)
            if latest_build == '':
                logging.error(f'No versions there {os.environ["SHARED_PATH"]}')
                return
            logging.info(f'Shared latest is {latest_build}')
            if os.path.isfile(last_build_rec):
                logging.info(f'Check the last build from {last_build_rec}.')
                with open(last_build_rec, 'r') as f:
                    local_latest = f.read().strip()
                logging.info(f'local latest is {local_latest}')
                if local_latest != '' and local_latest.strip().split('.')[-1] in os.path.basename(latest_build):
                    logging.info('No need to run due to no new version.')
                    return
            else:
                logging.warning(f'No last build record file {last_build_rec} found.')
                local_latest = 'not recorded'
            logging.info(f'The shared latest {latest_build} is different with local latest {local_latest}, download it.')
        else:
            latest_build = os.path.join(os.environ['SHARED_PATH'], f'{os.environ["SPE_NUM"]}.7z')
            logging.info(f'Specified number already given, download {latest_build}.')
        return latest_build

    def download_new_build(self, new_build):
        setup_dir = os.path.join(os.path.expanduser("~"), 'Downloads', f'setup_{self._prod.name}')
        if not os.path.isdir(setup_dir):
            os.mkdir(setup_dir)
        remove_folder(setup_dir, False)
        shutil.copy(new_build, setup_dir)
        zip_file = os.path.join(setup_dir, os.path.basename(new_build))
        logging.info(f'{zip_file} is downloaded successfully, extract it.')
        target_dir = zip_file.split(".7z")[0]
        unzip_file(zip_file, target_dir)
        setup_file = os.path.join(target_dir, f'_setup_{self._prod.alias}', 'shipped', 'Setup.exe')
        assert os.path.isfile(setup_file), f'{setup_file} does not exist after extracting.'
        return setup_file

    def uninstall_all(self):
        logging.info('Start uninstalling all.')
        uninstallation_flag = os.path.join(os.environ['TEMP'], 'UNINSTALL_SUCCESS')
        if os.path.isfile(uninstallation_flag):
            os.remove(uninstallation_flag)
        kill_process(self._prod.processName, True)
        path_name = os.path.join(self._installationRoot, 'simufact',
                                 f'Uninstall Simufact {self._prod.name.capitalize()}*.exe')
        try:
            uninstall_file = max((f for f in glob.iglob(path_name) if os.path.isfile(f)), key=os.path.getmtime)
        except:
            logging.warning(f'No uninstall file found in {path_name}.')
        else:
            cmd = f'"{uninstall_file}" /S'
            subprocess.call(cmd, shell=True)
            uninstaller_name = 'Un_A.exe'
            uninstaller_exists = False
            timeout = 60.0 * 3
            start = time.time()
            while True:
                if time.time() - start > timeout:
                    raise TimeoutError(f'Timeout waiting for {uninstaller_name} to appear in {timeout} seconds.')
                for pro in psutil.process_iter():
                    if uninstaller_name in pro.name():
                        uninstaller_exists = True
                        break
                if uninstaller_exists:
                    logging.info(f'{uninstaller_name} starts running.')
                    break
                else:
                    logging.warning(f'{uninstaller_name} has not appeared yet.')
                time.sleep(1.0)
            timeout = 60.0 * 30
            start = time.time()
            while True:
                if time.time() - start > timeout:
                    raise TimeoutError(f'Timeout waiting for {uninstaller_name} to disappear in {timeout} seconds.')
                for pro in psutil.process_iter():
                    if uninstaller_name in pro.name():
                        uninstaller_exists = True
                        break
                    else:
                        uninstaller_exists = False
                if not uninstaller_exists:
                    logging.info(f'{uninstaller_name} has disappeared.')
                    break
                else:
                    logging.warning(f'{uninstaller_name} is still running.')
                time.sleep(5.0)
            exe_name = os.path.join(self._installationRoot, 'simufact', self._prod.name, '*',
                                    'sfForming' if self._prod.name == 'forming' else '', 'bin', self._prod.processName)
            matches = glob.glob(exe_name)
            if len(matches) == 0:
                # add a flag to indicate uninstallation successful with cmd
                with open(uninstallation_flag, 'w') as wf:
                    wf.write('')
            else:
                logging.warning(f'Unattended uninstallation went wrong as {matches} is not empty.')

        if os.path.isdir(os.path.join(self._installationRoot, 'simufact')):
            remove_folder(os.path.join(self._installationRoot, 'simufact'), False)

        # if os.path.isdir(os.path.join(os.environ['APPDATA'], 'Simufact')):
        #     remove_folder(os.path.join(os.environ['APPDATA'], 'Simufact'), False)
        logging.info('Uninstall app successfully.')

    def async_install(self, setup_file: str, timeout=60.0*30):
        logging.info('Start installing.')
        if not os.path.exists(self._installationRoot):
            os.mkdir(self._installationRoot)
        paras = rf'/S /AcceptLicenseNotice=yes /{self._prod.name.capitalize()}=yes /Examples=yes /Demos=yes /Material=yes /Monitor=yes{" /Remote=yes" if self._prod.name == "forming" else ""} /D={self._installationRoot}'
        cmd = f'{setup_file} {paras}'
        logging.info(f'execute {cmd}')
        sub_p = subprocess.Popen(cmd, shell=True)
        start = time.time()
        try:
            while True:
                duration = time.time() - start
                res = sub_p.poll()
                if duration > timeout:
                    if res is not None:
                        sub_p.kill()
                    raise TimeoutError(f'Failed to install due to {timeout} timeout.')
                if res is None:
                    logging.warning('Installation is ongoing, check in the next loop.')
                else:
                    path_name = os.path.join(self._installationRoot, 'simufact', self._prod.name, '*',
                                 'sfForming' if self._prod.name == 'forming' else '', 'bin', self._prod.processName)
                    matches = glob.glob(path_name)
                    assert len(matches) < 2, f'Count of {matches} greater than 2.'
                    if len(matches) == 0:
                        logging.warning(f'Installation execution is over, but {path_name} does not exist.')
                    else:
                        logging.info(f'{path_name} has been matched, install app successfully.')
                        break
                time.sleep(5.0)
        except TimeoutError:
            logging.error(f'Filed to install, prune {self._installationRoot}.')
            self.uninstall_all()
            exit(-1)

    @staticmethod
    def record_build(new_build, build_rec):
        current_version = os.path.basename(new_build).strip().split(".7z")[0]
        with open(build_rec, 'w') as f:
            f.write(current_version)
        logging.info(f'Update the version to {build_rec} with {current_version}.')
        print(f'##vso[task.setvariable variable=LATEST_VERSION]{current_version}')

    def __call__(self):
        build_rec = self.get_build_rec()
        new_build = self.check_new_build(build_rec)
        if new_build is None:
            return
        setup_file = self.download_new_build(new_build)
        self.uninstall_all()
        self.async_install(setup_file)
        self.record_build(new_build, build_rec)


def main():
    args = sys.argv[1:]
    args_len = len(args)
    prod_name = None
    for i in range(args_len):
        if args[i] == '-p' and i+1 < args_len:
            prod_name = args[i+1]
            break
    if prod_name is None:
        logging.error(f'Product name is not defined with -p, the valid names are {", ".join(simufactIns.PROD_NAMES)}')
        sys.exit(-1)
    SilentInstallation(prod_name)()
    sys.exit(0)


if __name__ == '__main__':
    main()
