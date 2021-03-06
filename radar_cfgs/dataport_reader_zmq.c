#include <stdio.h>   /* Standard input/output definitions */
#include <string.h>  /* String function definitions */
#include <unistd.h>  /* UNIX standard function definitions */
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */
#include <time.h>
#include <stdbool.h>
#include <math.h>
#include <zmq.h> 	 /* ZMQ sockets, message passing library */

#define DATA_PORT_PATH "/dev/ttyACM1"

#define STDIN 	0
#define STDOUT	1

#define microSec_bwCommands 100000

#define READ_BUF_SIZE  500

//#define SEND_BUF_SIZE  15  /* 5+5+5, 4 digit characters for XYZ coordinates
							  //in centimetres */

#define UPDATE_RATE 100000

#define PORT "5557" /*To connect to Fusion Engine using ZMQ-Socket*/

#define SEND_SINGLE_SIZE 	15 	/* = 5+5+5, i.e. 5 integers for each X,Y,Z */

#define MAX_DETD_OBJS		10  /*Maximum No. of detected objects for sending to ZMQ server.*/

#define SEND_ALL_SIZE  (SEND_SINGLE_SIZE * MAX_DETD_OBJS + 1)


int openAndInit_dataport(void)
{
  int fd; /* File descriptor for the port */


  fd = open(DATA_PORT_PATH, O_RDONLY | O_NOCTTY | O_NDELAY);
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
  cfsetispeed(&SerialPortSettings,B921600);
  cfsetospeed(&SerialPortSettings,B921600);

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

	//tcflush(fd, TCIFLUSH);

	cfmakeraw(&SerialPortSettings);

	tcsetattr(fd, TCSANOW, &SerialPortSettings);

  return (fd);
}

int multiply(char* data){
	/*return (data[0]
		+ data[1]<<8
		+ data[2]<<16
		+ data[3]<<24);*/
    int sum =0;
     int size =4;
     int mult[]={1,pow(2,8),pow(2,16),pow(2,24)};
    for(int i=0;i<size;i++){
      sum = data[i]*mult[i]+sum;
}
   return sum;
 }

int multiplyTwo(char* data){
       /* return (data[0]
		+ data[1]<<8
		+ data[2]<<16
	+ data[3]<<24);*/
    int sum =0;
     int size =2;
     int mult[]={1,pow(2,8)};
    for(int i=0;i<size;i++){
      sum = data[i]*mult[i]+sum;
}
   return sum;
      
   }



/*int multiply (char data[],int size){
int sum =0;
//int mult[] ={pow(2,24),pow(2,16),pow(2,8),1};
int mult[]={1,pow(2,8),pow(2,16),pow(2,24)};
for(int i=0;i<size;i++){
 sum = data[i]*mult[i]+sum;
}
return sum;
}*/
/*int multiplytwoB(char data[],int size){
int sum =0;
int mult[] ={1,pow(2,8)};
for(int i=0;i<size;i++){
 sum = data[i]*mult[i]+sum;
}
return sum;
} */


bool isMagic(char data[], int size,int baseIndex){
if(size>=baseIndex+8){
return (data[baseIndex+0]==2&& data[baseIndex+1]==1&&data[baseIndex+2]==4&&data[baseIndex+3]==3&&data[baseIndex+4]==6&&data[baseIndex+5]==5&&data[baseIndex+6]==8&&data[baseIndex+7]==7);
}
return false;
}

void slice (int indexfrom, int indexto, char data[],char slice[]){
int j=0;
for(int i =indexfrom;i<=indexto;i++){
slice[j]=data[i];
j++;
}
}

void reshape(char shape[][10],char array[], int rows, int columns,int arrayLength){
int k =0;
for(int r=0;r<rows;r++){
char row[columns];

 for(int c=0;c<columns;c++){
    
   int i =c+k;
   if(i<arrayLength){
      row[c]=array[i];
    }  
   }//for
    int j=r;
    for(int i=0;i<columns;i++){
     
     shape[j][i]=row[i];
     }//for
}//Main For Loop
 k=k+columns;
}

int main(){

	int bytes_read; //from UART Data port
	char read_buffer[READ_BUF_SIZE];

	//char send_buffer[SEND_SINGLE_SIZE];
	char send_single[SEND_SINGLE_SIZE + 1];
	char send_all_buffer[SEND_ALL_SIZE];
	char buffer [10];
	int zmq_flags;
	int nbytes_tosend = 1; 	
	
	printf("\n Connecting to Fusion Engine ZMQ server\n\n");
    
    void *context = zmq_ctx_new ();
    void *requester = zmq_socket (context, ZMQ_REQ);
    zmq_connect (requester, "tcp://localhost:" PORT);


	// bytes_read = read(fd,&read_buffer,80);

    while(1){
  	int dataport_fd = openAndInit_dataport();


  	bytes_read = read(dataport_fd, &read_buffer, READ_BUF_SIZE);

	/*for (i = 0; i < bytes_read; i++){
		printf("%d ",read_buffer[i]);
	}*/

	printf("\n");

	//youssef's program goes here.
          //printf("My code starts here!!");
        int size = sizeof(read_buffer)/sizeof(read_buffer[0]);
       if (sizeof(read_buffer)/sizeof(read_buffer[0])>=8+4+4 && isMagic(read_buffer,size,0)){
       //PROCESS
       //The indecies were obtained using the given mmwave documentation and the UART output packet
	
	char packetLength[4];//jump
        slice(12,15,read_buffer,packetLength) ;
	int length = multiply(packetLength);
	//printf ("length is %d",length);
	//printf("\n");
	char numObjs[4];
        slice (28, 31,  read_buffer,numObjs);
	//printf("index zero is %i",numObjs[0]);
        int numdetectedObjs=multiply(numObjs);

	printf("number of detected objects is %d",numdetectedObjs);
        char numTLV [4];
	slice(32,35,read_buffer,numTLV);
	int numTLVs = multiply(numTLV);
	char tag[4];
	//slice(36,39,read_buffer,tag);
        slice(40,43,read_buffer,tag);
        int tagValue= multiply(tag);//tag should have a value of 1
        //printf("tag value is %d", tagValue);
	char jump1 [4];
	slice(44,47,read_buffer,jump1);
	int jump = multiply(jump1);
        char xyzformat[2];
        slice(50,51,read_buffer,xyzformat);
        int num = multiplyTwo(xyzformat);
        int xyzScale = pow(2,num);
        
       // printf("xyz scale is %d", xyzScale);
	int currentInd = 52;
	int numberObjs;
	for(int i=0;i<length;i++){
	if (tagValue==1){
		
	  //flush the send-all buffer.
			memset(send_all_buffer, 0, SEND_ALL_SIZE);
			nbytes_tosend = 1;	/*At least a NULL character to send */
	  
	  for(int j=0;j<numdetectedObjs;j++){
	   
	   currentInd = currentInd+6;
	   
	   char x[2] ;
           slice(currentInd,currentInd+1,read_buffer,x);
 	   double xV = multiplyTwo(x);
	   if(xV>32767){
		xV=xV-65536;
	   }
	   xV=xV/xyzScale;
	   printf("x coordinate %f",xV);// x coordinate
	   currentInd=currentInd +2;
	   char y[2];
	   slice(currentInd,currentInd+1,read_buffer,y);
	   double yV = multiplyTwo(y);
	   if(yV>32767){
		yV=yV-65536;
	   }
	   yV=yV/xyzScale;
	   printf(" Y coordinate %f ",yV); // y coordinate
           printf("\n");
	   currentInd = currentInd +2;
	   char z[2];
	   slice(currentInd,currentInd+1,read_buffer,z);
	   double zV = multiplyTwo(z);
	   if (zV>32767){
			zV=zV-65536;
		}
           zV=zV/xyzScale;
	   printf(" Z coordinate %f",zV);
           printf("\n");
           currentInd = currentInd + 2;
		
		//Send to Fusion Engine, xV, yV, zV.
		
		//sprintf(send_buffer, "%04.0f%04.0f%04.0f", xV*100, yV*100, zV*100);
		//printf("%04.0f%04.0f%04.0f\n", xV*100, yV*100, zV*100);
		
		if (i < MAX_DETD_OBJS){
			//craft a digit string for this single bounding box.
			memset(send_single, 0, SEND_SINGLE_SIZE + 1);
			//sprintf(send_single, "%04.0f%04.0f%04.0f%04.0f", bb[0], bb[1], bb[2], bb[3]);
			sprintf(send_single, "%05.0f%05.0f%05.0f", xV*100, yV*100, zV*100);

			//append to the send-all buffer.
			strncat(send_all_buffer, send_single, SEND_SINGLE_SIZE);
			nbytes_tosend += SEND_SINGLE_SIZE;
		}
		
		zmq_flags = 0;
		if ( (numdetectedObjs > 1) 				/*There are more than one detectedObjects */
			  && (j < numdetectedObjs - 1) )  	/*and This is Not the last detectedObject*/
		{
			zmq_flags = ZMQ_SNDMORE;
		}
		
		//zmq_send (requester, "Hello", 5, zmq_flags);
		//zmq_send (requester, send_buffer, SEND_BUF_SIZE, zmq_flags);
		//zmq_recv (requester, buffer, 10, 0);
		
	  }  
	  
		if (numdetectedObjs > 0) {
			zmq_send (requester, send_all_buffer, nbytes_tosend, 0);	
		} else {
			// No Object detected. Send a single NULL byte.
			zmq_send (requester, "\0", 1, 0);
		}
		zmq_recv (requester, buffer, 10, 0);
		
		break;//for 
	  
	  } else { //tag != 1
	    currentInd = currentInd+jump +2*4+1;//jump to the next tag
	    char tag[4];
	    slice(currentInd,currentInd+4,read_buffer,tag);
            char tagValue= multiply(tag);//new tag value
	      
	  }		
		
	}
	  
         		
	   } else {
      printf("invalid data\n");
       
       }
      
	close(dataport_fd);
	usleep(UPDATE_RATE);
   }// end while

	return 0;
}
