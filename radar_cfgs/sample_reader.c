#include <stdio.h>   /* Standard input/output definitions */
#include <string.h>  /* String function definitions */
#include <unistd.h>  /* UNIX standard function definitions */
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */

#define CFG_PATH "/home/shamoonirshad/Documents/radar_cfgs/cfg_1.txt"

#define STDIN 	0
#define STDOUT	1

int open_file(void)
{
  int fd; /* File descriptor for the port */


  fd = open(CFG_PATH, O_RDWR | O_NOCTTY | O_NDELAY);
  if (fd == -1)
  {
   /*
    * Could not open the port.
    */

    perror("open_port: Unable to open /dev/ttyf1 - ");
  }
  else
    fcntl(fd, F_SETFL, 0);

  return (fd);
}

int main(){

	char read_buffer[80];
	int bytes_read;

	// int fd = open_file();

	// bytes_read = read(fd,&read_buffer,80);
	FILE *fp;

    fp = fopen( CFG_PATH, "r" );


	while(NULL != fgets( read_buffer, 80, fp )){

		// printf("Read string = %s", read_buffer);
		write(STDOUT,read_buffer,strlen(read_buffer));

	}

	// close(fp);
	fclose(fp);


	return 0;
}
