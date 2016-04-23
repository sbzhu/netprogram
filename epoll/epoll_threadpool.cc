#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <time.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#include <pthread.h>
#include <errno.h>

#include <string>
#include <map>
#include <set>
#include <iostream>
using namespace std;


static const int  LISTEN_PORT = 8000;
static const char *  SERVER_IP = "127.0.0.1";

static const int  MAX_WORKER = 4;
static const int  MAX_EVENTS = 10;

typedef struct
{
	char	ip4[128];
	int		port;
	int		fd;
} listen_info;

typedef struct
{
	string request;
	string response;
} ConnectInfo;

class Worker {
	private:
		const int listendSocket;
		bool bRuning = false;
		int epoll = -1;
		set<int, ConnectInfo *> clientSocketSet;

	public:
		Worker(const int socket) : listendSocket(socket){ }
		void execute(); 
};

class Master {
	private:
		int listendSocket = -1;
		static map<int, Worker *> workerSet;

	public:

		void initListenSocket(){

		}

		// return if it's father
		bool createWorker(const int workerNum){
			while(workerSet.size() < workerNum)
			{
				int pid = fork();
				if(0 == pid) // the child
				{
					return false;
				} else if(pid > 0){ // the father
					workerSet[pid] = new Worker(listendSocket); 
				} else {
					cout << "fork error" << end;
					return true;
				} 
			}

			return true;
		}

		void execute(){

		}

		void keepAlive(){

		}

		int getListenSocket()
		{
			return listendSocket;
		}
};

int main(int argc, char * argv[])
{
	Master * master = new Master();
	master->initListenSocket();
	bool isParent = master->createWorker(MAX_WORKER);
	if(isParent)
	{

	}

	return 0;
}

