all: hello.c
	gcc hello.c -o hello_scalar
	gcc hello.c -o hello_sve -march=armv8-a+sve -O3
	gcc hello.c -o hello_neon -march=armv8-a -O3
test:
	rm -rf test_*
	$(HOME)/mywork/roofline/roofline.py record --trace_f multiply -o test_sve -- ./hello_sve
	$(HOME)/mywork/roofline/roofline.py record --trace_f multiply -o test_neon -- ./hello_neon
	$(HOME)/mywork/roofline/roofline.py record --trace_f multiply -o test_scalar -- ./hello_scalar
	cat test_*/roofline.csv
hello_time:
	gcc hello.c -DTIME_RUN -o hello
clean: hello hello_time
	rm hello hello_time
