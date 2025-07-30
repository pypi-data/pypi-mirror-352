# MySSIX Thing SDK for Python

[![PyPI version](https://badge.fury.io/py/big-thing-py.svg)](https://badge.fury.io/py/big-thing-py)

이 문서에서는 `MySSIX IoT Platform`의 Thing Python SDK를 소개합니다. `Thing`은 `MySSIX IoT Platform`에서 사용되는 기능의 단위인 `Service`를 제공하는 제공자입니다. 이 문서를 통해 `Thing`을 실행하고 개발하는 방법에 대해 알 수 있습니다.

`MySSIX IoT Platform`에서 `Thing`은 크게 2가지로 나뉩니다.

1. **Big Thing**
2. **Small Thing**

이 문서에서는 Python으로 작성된 **Big Thing** 어플리케이션을 실행하고 개발하는 방법에 대해 설명합니다. **Small Thing**에 대해서는 [Small Thing](https://github.com/sopiot/small-thing)을 참고해주세요.

## Getting Started

### Prerequisites

해당 SDK를 사용하기 위해서는 다음과 같은 요구사항을 만족해야합니다.

- Python 3.10+

### Install from PyPI

```bash
pip3 install big-thing-py
```

### Install from source

```bash
git clone https://github.com/sopiot/big-thing-py.git
cd big-thing-py
pip3 install .
# 만약 Thing SDK를 개발하고자 한다면 다음의 명령어를 사용합니다.
# -e 옵션을 사용하면 레포지토리의 코드 변경사항이 바로 Thing 동작에 반영됩니다.
# pip3 install -e .
```

### Usage

예제를 실행하기 전에 `MySSIX IoT Platform`의 `Middleware`를 먼저 실행해야 합니다.

#### Middleware Docker 이미지 다운로드 & 실행

```bash
docker pull sopiot/sopiot_middleware_ubuntu1804_x64
docker run -it -d --name sopiot_middleware -p 1883:1883 -p 1884:1884 -p 8883:8883 -p 8884:8884 -p 58132:58132 sopiot/sopiot_middleware_ubuntu1804_x64
```

이후, 다음의 명령어를 통해 기본 예제를 실행할 수 있습니다.

```bash
python3 samples/big_thing/basic_test/run.py
```

만약 가상환경을 생성하여 예제를 실행하려는 경우 `pipenv`를 사용할 수 있습니다. 우선, 다음 명령어로 `pipenv`를 설치합니다.

```bash
pip install pipenv --upgrade
```

`pipenv` 가상환경을 생성 및 레포지토리로부터 패키지를 설치합니다.

```bash
pipenv install -e .
```

그리고, 다음의 명령어를 통해 기본 예제를 실행할 수 있습니다.

```bash
pipenv run python samples/big_thing/basic_test/run.py
```

`Thing`이 `Middleware`에 등록되면 `Thing`의 `Service`를 `Scenario`를 통해 사용할 수 있습니다. `Scenario`는 `MySSIX IoT Platform`의 [Web Client App](http://iotdev.snu.ac.kr:3014/)을 통해 조작 및 생성할 수 있습니다. -> _따로 Documents 폴더를 생성하여 Web Client App와 관련한 README를 작성해야하는 것이 좋아보임_.

#### Systemd Service 등록

`Thing`을 `Systemd` 서비스로 등록하여 `Thing`이 부팅 시 자동으로 실행되도록 할 수 있습니다.
`Thing`을 `Systemd` 서비스로 등록하기 위해서 다음의 단계를 따릅니다.

1. 실행할 예제를 정하여 다음의 명령어를 실행.

```bash
./install_systemd.sh --system-name <service_name> samples/big_thing/<sample_name>/run.py <run.py_arguments>
# or with default system name 'thing'
./install_systemd.sh samples/big_thing/<sample_name>/run.py <run.py_arguments>
```

2. `Thing`이 서비스로 등록되었는지 확인.

```bash
sudo service <service_name> status
```

or

```bash
journalctl -u <service_name>.service -f
```

3. `Thing` 서비스 삭제

```bash
./uninstall_systemd.sh <service_name>
```

### PyPI 배포

먼저 PyPI 계정에 접속한 후, `Account settings` 에서 `API tokens` - `Add API token` 을 통해 PyPI API 토큰을 생성합니다.

다음의 명령어를 통해 `poetry`에 PyPI API 토큰을 설정합니다.

```bash
poetry config pypi-token.pypi <your_pypi_api_token>
```

이후 다음 명령어로 PyPI에 배포합니다.

```bash
poetry publish --build
```

## Samples

[Samples README](samples/README.md)

## Contributions

## License
