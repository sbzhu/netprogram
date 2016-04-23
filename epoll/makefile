all : epoll_threadpool tinyenginx
epoll_threadpool : epoll_threadpool.cc
	g++ epoll_threadpool.cc -lpthread -std=c++11  -o epoll_threadpool
tinyenginx : tinyenginx.cc 
	g++ tinyenginx.cc -lpthread -std=c++11 -o tinyenginx 
