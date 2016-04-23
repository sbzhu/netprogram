#include <iostream>
#include <set>
#include <signal.h>
#include <sys/select.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>

#include <sys/mman.h>
#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

#define GET_ARRAY_LEN(array) (sizeof(array) / sizeof(array[0]))
#define PROCESS_NUM 4

// Create the listen socket
int startup(int port) {
	struct sockaddr_in servAddr;
	memset(&servAddr, 0, sizeof(servAddr));
	servAddr.sin_family = AF_INET;
	//��Ĭ������
	servAddr.sin_addr.s_addr = htonl(INADDR_ANY);
	//�˿�
	servAddr.sin_port = htons(port);
	int listenFd;
	//�����׽���
	if ((listenFd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
		printf("create socket error: %s(errno: %d)\n",strerror(errno),errno);
		return 0;
	}
	unsigned value = 1;
	setsockopt(listenFd, SOL_SOCKET, SO_REUSEADDR, &value, sizeof(value));
	//���׽���
	if (bind(listenFd, (struct sockaddr *)&servAddr, sizeof(servAddr))) {
		printf("bind socket error: %s(errno: %d)\n",strerror(errno),errno);
		return 0;
	}
	//��ʼ���������������������
	if (listen(listenFd, 10) == -1) {
		printf("listen socket error: %s(errno: %d)\n",strerror(errno),errno);
		return 0;
	}
	return listenFd;
}

//�����ӽ��̵����飬��������м����ӽ���
static int processArr[PROCESS_NUM];
//�������ɸ��ӽ��̣����ص�ǰ�����Ƿ񸸽���
bool createSubProcess() {
	for (int i=0; i<GET_ARRAY_LEN(processArr); i++) {
		int pid = fork();
		//������ӽ��̣�����0
		if (pid == 0) {
			return false;
		}
		//����Ǹ����̣�����fork
		else if (pid >0){
			processArr[i] = pid;
			continue;
		}
		//�������
		else {
			fprintf(stderr,"can't fork ,error %d\n",errno);
			return true;
		}
	}
	return true;
}

//�źŴ���
void handleTerminate(int signal) {
	for (int i=0; i<GET_ARRAY_LEN(processArr); i++) {
		kill(processArr[i], SIGTERM);
	}
	exit(0);
}

//����http����
bool handleRequest(int connFd) {
	if (connFd<=0) return false;
	//��ȡ����
	char buff[4096];
	//��ȡhttp header
	int len = (int)recv(connFd, buff, sizeof(buff), 0);
	if (len<=0) {
		return false;
	}
	buff[len] = '\0';
	std::cout<<buff<<std::endl;

	return true;
}

//������
pthread_mutex_t *mutex;
//���������mutex
void initMutex()
{
	//���û�����Ϊ���̼乲��
	mutex=(pthread_mutex_t*)mmap(NULL, sizeof(pthread_mutex_t), PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
	if( MAP_FAILED==mutex) {
		perror("mutex mmap failed");
		exit(1);
	}
	//����attr������
	pthread_mutexattr_t attr;
	pthread_mutexattr_init(&attr);
	int ret = pthread_mutexattr_setpshared(&attr,PTHREAD_PROCESS_SHARED);
	if(ret != 0) {
		fprintf(stderr, "mutex set shared failed");
		exit(1);
	}
	pthread_mutex_init(mutex, &attr);
}

int main(int argc, const char * argv[])
{
	int listenFd;

	initMutex();
	//���ö˿ں�
	listenFd = startup(8080);

	//�������ɸ��ӽ���
	bool isParent = createSubProcess();
	//����Ǹ�����
	if (isParent) {
		while (1) {
			//ע���źŴ���
			signal(SIGTERM, handleTerminate);
			//����ȴ��ź�
			pause();
		}
	}
	//������ӽ���
	else {
		//�׽��ּ���
		fd_set rset;
		//����׽���
		int maxFd = listenFd;
		std::set<int> fdArray;
		//ѭ�������¼�
		while (1) {
			FD_ZERO(&rset);
			FD_SET(listenFd, &rset);
			//��������ÿ����Ҫ�������׽���
			for (std::set<int>::iterator iterator=fdArray.begin();iterator!=fdArray.end();iterator++) {
				FD_SET(*iterator, &rset);
			}
			//��ʼ����
			if (select(maxFd+1, &rset, NULL, NULL, NULL)<0) {
				fprintf(stderr, "select error: %s(errno: %d)\n",strerror(errno),errno);
				continue;
			}

			//����ÿ�������׽���
			for (std::set<int>::iterator iterator=fdArray.begin();iterator!=fdArray.end();) {
				int currentFd = *iterator;
				if (FD_ISSET(currentFd, &rset)) {
					if (!handleRequest(currentFd)) {
						close(currentFd);
						fdArray.erase(iterator++);
						continue;
					}
				}
				++iterator;
			}
			//������Ӽ����׽���
			if (FD_ISSET(listenFd, &rset)) {
				if (pthread_mutex_trylock(mutex)==0) {
					int newFd = accept(listenFd, (struct sockaddr *)NULL, NULL);
					if (newFd<=0) {
						fprintf(stderr, "accept socket error: %s(errno: %d)\n",strerror(errno),errno);
						continue;
					}
					//���������׽���
					if (newFd>maxFd) {
						maxFd = newFd;
					}
					fdArray.insert(newFd);
					pthread_mutex_unlock(mutex);
				}
			}
		}
	}

	close(listenFd);
	return 0;
}
