import os
import logging

from jupyter_server.auth  import passwd
logging.basicConfig(level=logging.INFO)


# 환경 변수 읽기
notebook_port = int(os.getenv('JUPYTER_PORT'))
notebook_dir = os.getenv('JUPYTER_DIR')
notebook_password = os.getenv('JUPYTER_NOTEBOOK_PASSWORD')
notebook_app_allow_origin = os.getenv('JUPYTER_APP_ALLOW_ORIGIN')
notebook_app_ip = os.getenv('JUPYTER_APP_IP')
notebook_token = os.getenv('JUPYTER_TOKEN')
port_retries = os.getenv('PORT_RETRIES')

# 환경 변수 출력 (디버깅용)
logging.info(f"notebook_port: {notebook_port}")
logging.info(f"notebook_dir: {notebook_dir}")
logging.info(f"notebook_password: {notebook_password}")
logging.info(f"notebook_app_allow_origin: {notebook_app_allow_origin}")
logging.info(f"notebook_app_ip: {notebook_app_ip}")
logging.info(f"port_retries: {port_retries}")

c = get_config()  #noqa
c.ServerApp.allow_origin = notebook_app_allow_origin  # 외부 접속 허용하기
c.ServerApp.ip = notebook_app_ip  #아이피 설정
c.ServerApp.notebook_dir = notebook_dir
c.ServerApp.open_browser = False # 시작 시 서버PC에서 주피터 노트북 창이 열릴 필요 없음
c.ServerApp.password = passwd(notebook_password)
c.ServerApp.port = notebook_port   #포트 설정
c.port_retries = port_retries
c.NotebookApp.token = notebook_token