from genericpath import exists
from os import chmod, system, unlink, write
from shutil import rmtree
import logging

import typer

from stack.config import stack_exists, stack_path

service_app = typer.Typer()

log = logging.getLogger('rich')


def service_name(stack: str):
    return f"podman-stack__{stack}"

@service_app.command('name')
def name_cmd(stack: str):
    print(service_name(stack))

def service_file(stack: str):
    return f"/etc/systemd/system/{service_name(stack)}.service"

def service_exists(stack: str):
    return exists(service_file(stack))

def service_template(stack: str):
    return f"""
[Unit]
Description=Stack service for {stack}
After=network.target

[Service]
Restart=always

User={service_name(stack)}
Group={service_name(stack)}

ExecStart=stack up {stack}
ExecStop=stack down {stack}

[Install]
WantedBy=multi-user.target
"""

def setup_user_perms(stack: str):
    system(f'useradd -d{stack_path(stack)} {service_name(stack)}')
    system(f'chgrp -R {service_name(stack)} {stack_path(stack)}')
    system(f'chmod g+r-w,o-rw {stack_path(stack)}')

@service_app.command('create')
def setup_service(stack: str):
    if not stack_exists(stack):
        log.error(f'Stack {stack} does not exist.')
        return 1

    service = service_name(stack)
    if system(f'users | grep {service}') != 0:
        log.info(f'Creating user {service} and assigning permissions...')
        setup_user_perms(stack)
    
    if service_exists(stack):
        log.info(f'Creating service {service}.service...')
        log.error(f'Service {service} already exists - if you want to recreate it, run stack service delete {stack} first.')
        return 1
    
    with open(service_file(stack)) as f:
        f.write(service_template(stack))
    
    return 0

@service_app.command('delete')
def delete_service(stack: str):
    service = service_name(stack)
    if not service_exists(stack):
        log.error(f'Service {service} does not exist.')
        return 1


    log.info(f'Stopping and disabling {service}.service...')
    stop_service(stack)
    disable_service(stack)

    log.info(f'Deleting service {service}.service...')
    unlink(service_file(stack))

    log.info(f'Deleting user {service} and group {service}...')
    system(f'userdel {service}')
    system(f'groupdel {service}')



@service_app.command('start')
def start_service(stack: str):
    return system(f'systemctl start {service_name(stack)}.service')

@service_app.command('stop')
def stop_service(stack: str):
    return system(f'systemctl stop {service_name(stack)}.service')

@service_app.command('enable')
def enable_service(stack: str):
    return system(f'systemctl enable {service_name(stack)}.service')

@service_app.command('disable')
def disable_service(stack: str):
    return system(f'systemctl disable {service_name(stack)}.service')