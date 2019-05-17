/***********************************************
 * wateringSensor.ino                          *
 * Created on : 17.05.2019                     *
 * Author     : Felix Fleckenstein             *
 * License    : GPL2                           *
 *                                             *
 * Description:                                *
 * 		Reads values from DH11 and moisture-   *
 *		sensors and sends it to server         *
 ***********************************************/

#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include "extLib/DHT.h"

/***********************************************
 * CONFIG PART BEGIN                           *
 ***********************************************/
#define WLAN_SSID "straightAhead"					      	//WLAN SSID
#define WLAN_KEY "uLVBcdiOq60Qzo9n2GVqs2"		    	//WLAN Password
#define SERVER_ADDRESS "http://192.169.1.19:8080"	//Address of server backend including port

#define DELAY 1		  		// Delay between sensor readings
 
#define MOISTURE_IN		A0		//Analog Pin 0 for reading the moisture-sensor value
#define MOISTURE_POWER	14		//D5 for powering moisture-sensor
#define DHT11_IN		0		//D3 pin for reading the temperature and humidity values
#define DHT11_POWER		5		//D1 for powering DHT11-sensor

#define DRY 816			//measured dry value during calibration (measured in air) 
#define WET 350			//measured wet value during calibration (measured in water)

/***********************************************
 * CONFIG PART END                             *
 ***********************************************/

 /***********************************************
 * sends messured values to backend server      *
 ***********************************************/
void sendWiFi(String typ, float value) {
  if(WiFi.status()== WL_CONNECTED){   //Check WiFi connection status
     
    HTTPClient http;    //Declare object of class HTTPClient
    
    http.begin(String(SERVER_ADDRESS) + "/add?" + typ + "=" + String(value, 2));      //Specify request destination
    http.addHeader("Content-Type", "text/plain");  //Specify content-type header
     
    int httpCode = http.POST("");       //Send the request
    String payload = http.getString();  //Get the response payload
     
    Serial.println(httpCode);   //Print HTTP return code
    Serial.println(payload);    //Print request response payload
     
    http.end();  //Close connection
  }else{
     Serial.println("Error in WiFi connection");   
  }
}

 /***********************************************
 * reads moisture sensor and send to server     *
 ***********************************************/
void readMoistureSensor() {
  digitalWrite(MOISTURE_POWER, HIGH);
  delay(500);

  //Sensor Wert einlesen
  float sensorValue = analogRead(MOISTURE_IN);  
  digitalWrite(MOISTURE_POWER, LOW);

  float moisture = (100 - ((sensorValue-WET)/(DRY-WET)*100));
  if(moisture > 100) {
    moisture = 100;
  }
  else if(moisture < 0) {
    moisture = 0;
  }

  sendWiFi("moisture", moisture);
}

 /***********************************************
 * reads temperature sensor and send to server     *
 ***********************************************/
void readTemperature() {
  digitalWrite(DHT11_POWER, HIGH);
  delay(2000);
  DHT dht(DHT11_IN, 11);
  dht.begin();
  
  
  sendWiFi("temperature", dht.readTemperature());
  sendWiFi("humidity", dht.readHumidity());

  digitalWrite(DHT11_POWER, LOW);
}

/***********************************************
 * Setup function                              *
 ***********************************************/
void setup() {
  pinMode(MOISTURE_POWER, OUTPUT);
  pinMode(DHT11_POWER, OUTPUT);
  pinMode(MOISTURE_IN, INPUT);
}

/***********************************************
 * Starts WLAN for sending sensor values       *
 ***********************************************/
void startWiFi() {
  WiFi.begin(WLAN_SSID, WLAN_KEY);   //WiFi connection
  while (WiFi.status() != WL_CONNECTED) {  //Wait for the WiFI connection completion
    delay(500);
  }
}

/***********************************************
 * Stops WLAN for power reduction              *
 ***********************************************/
void stopWiFi() {
  WiFi.disconnect(true);	//Stops WiFi and reduce power consumption
  WiFi.mode( WIFI_OFF );
  WiFi.forceSleepBegin();
}

/***********************************************
 * Main-Loop                                   *
 ***********************************************/
void loop() {
  startWiFi();          //starts WiFi
  readMoistureSensor(); //read and send moisture value
  readTemperature();    //read and send temperature and humidity
  stopWiFi();           //stops WiFi for power reduction

  //pinMode(D0, WAKEUP_PULLUP);
  //ESP.deepSleep(60 * 30 * 1000000);
  delay(60 * DELAY * 1000);	//delay before next reading
}
