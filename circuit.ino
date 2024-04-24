//arduino file

int DC = 9;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(DC, OUTPUT);

}

void loop() {
  //speed up
  for(int x = 0; x<=255;x+=51){
    Serial.print(String(x) + ",");
    analogWrite(DC,x);
    delay(5000);
  }
  delay(5000);
  for(int x = 255; x>=0; x-=51){
    Serial.print(String(x) + ",");
    analogWrite(DC,x);
    delay(5000);
  }
  Serial.println("");
  delay(5000);
  
}
