# admin-drf
## 开源运维平台

drf:
![](https://www.coderops.net/media/image/active/20180830drf.png)

doc:
![](https://www.coderops.net/media/image/active/20180830doc.png)


此版本为开发版，用于研究与学习！

#### 安装python 3.6

##### 1 安装依赖

```bash
sudo yum -y install openssl-devel readline-devel 
```



##### 2 下载并安装python

```bash
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
tar -xzf Python-3.6.6.tgz 
cd Python-3.6.6
./configure --prefix=/usr/local/python36
sudo make
sudo make install
```


##### 3 配置pip

```bash
sudo tee /etc/pip.conf <<EOF
[global]
index-url = http://pypi.douban.com/simple
trusted-host = pypi.douban.com
[list]
format=columns
EOF
```


##### 4 安装与初始化virtualenv

```bash
sudo /usr/local/python36/bin/pip3 install virtualenv
/usr/local/python36/bin/virtualenv ~/python36env
```


#### 安装数据库

##### 安装mariadb

```bash
sudo yum -y install mariadb mariadb-server mariadb-devel
```


##### 配置mariadb

修改/etc/my.cnf，在[mysqld]下面增加如下几行配置

```ini
[mysqld]
default-storage-engine = innodb
innodb_file_per_table           
collation-server = utf8_general_ci
init-connect = 'SET NAMES utf8'
character-set-server = utf8
```



##### 起动服务

```bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
```


##### 初始化mariadb

这里设置root密码为 123456

```bash
mysql_secure_installation
```



##### 创建数据库

```bash
mysql -uroot -p123456 -e "create database ops CHARACTER SET utf8;"
```


#### 部署

##### 下载源码

```bash
cd ~
git clone https://github.com/syklinux/admin-drf.git
```



##### 安装依赖包

```
cd admin-drf/
pip install -r requirements.txt 
```



##### 修改配置文件

配置文件路径在 admin-drf/ops/settings.py 



配置mysql

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "ops",
        'USER': 'root',
        'PASSWORD': "123456",
        'HOST': "127.0.0.1",
        'PORT': "3306",
        'OPTIONS': {
            'init_command': "SET storage_engine=INNODB;SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```



##### 同步表结果

在操作之前需要在目录下创建一个logs的目录用于存放日志

```
mkdir logs
```


先生成user的迁移文件，然后同步

```bash
source ~/python36env/bin/activate
python manage.py makemigrations users
python manage.py migrate
```



接下来同步其它app的表结构

```bash
python manage.py makemigrations cabinet idcs manufacturers menu products servers sqlmng workorder
python manage.py migrate idcs
python manage.py migrate cabinet
python manage.py migrate manufacturers
python manage.py migrate products
python manage.py migrate menu
python manage.py migrate servers
python manage.py migrate sqlmng
python manage.py migrate workorder
```


##### 创建管理员用户
```bash
python manage.py createsuperuser --username admin --email admin@domain.com
```



##### 同步菜单

```bash
python scripts/import_menu.py
```


##### 起动服务

```
python manage.py runserver 0.0.0.0:8000
```

接下来就可以访问啦： 

http://your-ip:8000/    api root


http://your-ip:8000/docs/   api 文档


## sql上线
需要安装inception
```
https://github.com/mysql-inception/inception
```
注意bison版本，centos7如果yum安装bison，会因为版本过高导致编译报错
#### 一、安装依赖
```
yum -y install cmake libncurses5-dev libssl-dev g++ bison gcc gcc-c++ openssl-devel ncurses-devel mysql MySQL-python
wget http://ftp.gnu.org/gnu/bison/bison-2.5.1.tar.gz
tar -zxvf bison-2.5.1.tar.gz
cd bison-2.5.1
./configure
make
make install
```
#### 安装 inception
```
cd /usr/local/
wget https://github.com/mysql-inception/inception/archive/master.zip
unzip master.zip
cd inception-master/
sh inception_build.sh builddir linux
```

#### 三、修改配置
```
vi /etc/inc.cnf
###################
[inception]
general_log=1
general_log_file=inc.log
port=6669
socket=/tmp/inc.socket
character-set-client-handshake=0
character-set-server=utf8   
inception_remote_system_password=123456      
inception_remote_system_user=root    
inception_remote_backup_port=3306    
inception_remote_backup_host=127.0.0.1   
inception_support_charset=utf8
inception_enable_nullable=0
inception_check_primary_key=1
inception_check_column_comment=1
inception_check_table_comment=1
inception_osc_min_table_size=1
inception_osc_bin_dir=/usr/bin
inception_osc_chunk_time=0.1
inception_ddl_support=1
inception_enable_blob_type=1
inception_check_column_default_value=1
###################
```

#### 四、启动
```
$ nohup inception/debug/mysql/bin/Inception --defaults-file=/etc/inc.cnf &
```

#### 五、客户端连接
```
mysql -uroot -h127.0.0.1 -P 6669
MySQL [(none)]> inception get variables;
+------------------------------------------+-------------------------------------------+
| Variable_name                            | Value                                     |
+------------------------------------------+-------------------------------------------+
| autocommit                               | OFF                                       |
| bind_address                             | *                                         |
| character_set_system                     | utf8                                      |
。。。 。。。
```

#### pymysql包改造
修改pymysql/cursors.py 352行，改为：
```
if not self._defer_warnings:
    # self._show_warnings()
    pass
```
修改pymysql/connections.py 781行：改为：
```
def _request_authentication(self):
    if self.server_version.split('.', 1)[0] ==  'Inception2':
        self.client_flag |= CLIENT.MULTI_RESULTS
    elif int(self.server_version.split('.', 1)[0]) >= 5:
        self.client_flag |= CLIENT.MULTI_RESULTS
```

#### 备份库需要设置如下：
线上mysql需要配置如下：
```
bin-log=mysql-bin
binlog_format = MIXED
server-id =1 
```



## zabbix
zabbix是直接关联到数据库操作数据库的，该版本只适用于zabbix3.4。不需要migrate zabbix这个app。


## 服务器数据格式化
```json
{
    "hostname": "vm-mengdian-api-01",
    "os": "centos6.5",
    "manufacturer": "kvm",
    "model_name": "kvm",
    "uuid": "ASYDIA7SD89ASDASDHO",
    "server_cpu": "4",
    "server_mem": "128",
    "disk": "500G",
    "device": [
        {
            "name":"eth0",
            "ips":[
                {"ip_addr":"10.10.10.10","netmask":"255.255.255.0"}
            ],
            "mac":"00:00:00:00:00:01"
        }   
    ],
    "sn": "ASUDIOASD",
    "manage_ip": "10.10.10.10"
}
```
