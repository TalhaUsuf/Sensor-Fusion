#include <stdio.h>   /* Standard input/output definitions */
#include <string.h>  /* String function definitions */
#include <unistd.h>  /* UNIX standard function definitions */
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */
#include <time.h>

#define CFG_PORT_PATH "/dev/ttyACM0"

#define STDIN 	0
#define STDOUT	1

#define microSec_bwCommands 100000 

int openAndInit_cfgport(void)
{
  int fd; /* File descriptor for the port */


  fd = open(CFG_PORT_PATH, O_RDWR | O_NOCTTY | O_NDELAY);
  if (fd == -1){
   /*
    * Could not open the port.
    */

    perror("open_port: Unable to open cfg port - \n");

  } else {
    fcntl(fd, F_SETFL, 0);
  }

  struct termios SerialPortSettings;
  tcgetattr(fd, &SerialPortSettings);

  //setting the baud rate.
  cfsetispeed(&SerialPortSettings,B115200);
  cfsetospeed(&SerialPortSettings,B115200);

  // No Parity bit
  SerialPortSettings.c_cflag &= ~PARENB;   

  //One Stop bit
  SerialPortSettings.c_cflag &= ~CSTOPB;

  //8 data bits
  SerialPortSettings.c_cflag &= ~CSIZE; /* Clears the Mask       */
  SerialPortSettings.c_cflag |=  CS8;   /* Set the data bits = 8 */

  //Turn off hardware based flow control (RTS/CTS).
  SerialPortSettings.c_cflag &= ~CRTSCTS;

  //Turn on the receiver of the serial port
  SerialPortSettings.c_cflag |= CREAD | CLOCAL;

  //Turn off software based flow control (XON/XOFF).
  SerialPortSettings.c_iflag &= ~(IXON | IXOFF | IXANY);

  //Enable Cannonical mode (R/W Line by line, i.e. '\n' sensitive)
  SerialPortSettings.c_iflag &= ~(ICANON | ECHO | ECHOE | ISIG);


  return (fd);
}

int main(){




  int cfgport_fd = openAndInit_cfgport();

	

		// printf("Read string = %s", read_buffer);
		//write(STDOUT,read_buffer,strlen(read_buffer));
    write(cfgport_fd,"sensorStop\r",11);


	

	

	// close(fp);
	close(cfgport_fd);


	return 0;
}
