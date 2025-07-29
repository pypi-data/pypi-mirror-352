import urwid
import shutil
from subprocess import run, PIPE
import shlex
# import logging
import re
# import os

# os.unlink('example.log')

# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

gcloud_cmd = shutil.which("gcloud")
if not gcloud_cmd:
    raise OSError('gcloud를 찾을 수 없습니다')

program_top_menus = []

# Gcloud account status는 gcloud auth list 결과를 읽어 key를 주면 활성화 상태인지 아닌지 알려주고 프로젝트 변경도 가능해야 한다
class GCloudAuthStatus:
    def __init__(self) -> None:
        self.__account_list = {}
    
    def status_load(self):
        # global loop
        # loop.stop()
        gcloud_auth_list = run(shlex.split("gcloud auth list"), stdout=PIPE, stderr=PIPE)
        if gcloud_auth_list.stdout:
            for account_item in gcloud_auth_list.stdout.decode('utf-8').splitlines()[2:]:
                activate_account, account_address = re.match(r'(\*?)\s+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]*)', account_item).groups()
                self.__account_list[account_address] = {'activate': activate_account.startswith('*')}
        # loop.start()
    
    def __getitem__(self, account):
        if account not in self.__account_list:
            return KeyError('The account that requested activation is not logged into gcloud.')
        
        return self.__account_list[account]['activate']
    
    def activate(self, account):
        if account not in self.__account_list:
            raise ValueError('The account that requested activation is not logged into gcloud.')
        
        global loop
        loop.stop()
        run(shlex.split(f"gcloud config set account {account}"), stdout=PIPE, stderr=PIPE)
        loop.start()

        return True

    def getlist(self):
        return self.__account_list.keys()


account_checker = GCloudAuthStatus()
account_checker.status_load()

program_top_menus.extend(account_checker.getlist())
program_top_menus.append('New Google account login')

palette = [('reversed', 'standout', ''),
           ('bg', 'white', 'dark blue')]


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    elif key == 'left':
        back(None)


def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', account_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


class ProjectSelector:
    def __init__(self) -> None:
        self.__project_list = {}

    def load_project_list(self):
        global loop
        loop.stop()
        # Billing Quota 프로젝트가 설정되어 있는 경우 프로젝트 목록을 가져오는 메서드가 오동작 하므로 미리 해제해둔다
        run(shlex.split("gcloud config unset billing/quota_project"), stdout=PIPE, stderr=PIPE)

        gcloud_project_list_cmd = run(shlex.split("gcloud projects list"), stdout=PIPE, stderr=PIPE)
        gcloud_project_list = gcloud_project_list_cmd.stdout.decode('utf-8').splitlines()

        project_header_split_pos = [0, gcloud_project_list[0].index('NAME'), gcloud_project_list[0].index('PROJECT_NUMBER')] 
        
        for row in gcloud_project_list[1:]:
            project_id = row[project_header_split_pos[0]:project_header_split_pos[1]].strip()
            project_name = row[project_header_split_pos[1]:project_header_split_pos[2]].strip()
            project_number = row[project_header_split_pos[2]:].strip()
            self.__project_list[project_name] = {'id': project_id, 'number': project_number}
        
        loop.start()
        
    def activate(self, project_name):
        if project_name not in self.__project_list:
            raise ValueError('The project you requested to activate cannot be found in gcloud.')
        
        global loop
        loop.stop()
        run(shlex.split(f"gcloud config set project {self.__project_list[project_name]['id']}"), stderr=PIPE, stdout=PIPE)
        loop.start()

        return True

    def getlist(self):
        return self.__project_list.keys()


project_selector = ProjectSelector()
    

def account_chosen(button, choice):
    if button.get_label() == "New Google account login":
        gcloud_auth_login = run(shlex.split("gcloud auth login"), stdout=PIPE, stderr=PIPE)
        logined_account = next(filter(lambda x: x.startswith(b'You are now logged in as'), gcloud_auth_login.stderr.splitlines()))
        choice = logined_account.removeprefix(b"You are now logged in as [").removesuffix(b"].").decode('utf-8')

    # 현재 로그인 중인 계정이 선택한 계정과 같지 않으면 계정을 선택하도록 해야 한다
    account_checker.status_load()
    if not account_checker[choice]:
        account_checker.activate(choice)
    
    project_selector.load_project_list()
    project_list = project_selector.getlist()

    response = urwid.Text([f'You chosee Project ', f'[{choice}]', u'\n'])

    choice_project = [response]
    for project in project_list:
        button = urwid.Button(project)
        urwid.connect_signal(button, 'click', project_select, project)
        choice_project.append(urwid.AttrMap(button, 'bg', focus_map='reversed'))

    main.original_widget = urwid.Filler(urwid.Pile(choice_project), valign='top')


def project_select(button, project):
    project_selector.activate(project)
    raise urwid.ExitMainLoop()


def exit_program(button):
    raise urwid.ExitMainLoop()


def back(button):
    global main
    main.original_widget = menu('Select the Google account you want to use.', program_top_menus)


loop = None
main = None

def program_run():
    global main
    global loop

    main = urwid.Padding(menu('Select the Google account you want to use.', program_top_menus), left=2, right=2)
    main = urwid.AttrMap(main, 'bg')
    top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
        align='center', width=('relative', 100),
        valign='middle', height=('relative', 100),
        min_width=20, min_height=9)
    loop = urwid.MainLoop(top, palette=palette, unhandled_input=exit_on_q)
    loop.run()
