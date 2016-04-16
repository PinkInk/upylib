#http://eleccelerator.com/tutorial-about-usb-hid-report-descriptors/


#http://www.microchip.com/forums/m297214.aspx
/** I N C L U D E S *************************************************/
 #include "system\typedefs.h"
 #include "system\usb\usb.h"

/** C O N S T A N T S ************************************************/
 #pragma romdata

/* Device Descriptor */
rom USB_DEV_DSC device_dsc=
 {
     sizeof(USB_DEV_DSC),    // Size of this descriptor in bytes
     DSC_DEV,                // DEVICE descriptor type
     0x0200,                 // USB Spec Release Number in BCD format
     0x00,                   // Class Code
     0x00,                   // Subclass code
     0x00,                   // Protocol code
     EP0_BUFF_SIZE,          // Max packet size for EP0, see usbcfg.h
     0x04D8,                 // Vendor ID
     0x0049,                 // Product ID
     0x0000,                 // Device release number in BCD format
     0x01,                   // Manufacturer string index
     0x02,                   // Product string index
     0x00,                   // Device serial number string index
     0x01                    // Number of possible configurations
 };

 static rom byte cfg01[] =
 {
   0x09, 0x02, 0x65, 0x00, 0x02, 0x01, 0x00, 0x00, 0x32, // Config
   0x09, 0x04, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, // Interface 0
   0x09, 0x24, 0x01, 0x00, 0x01, 0x09, 0x00, 0x01, 0x01, // CS Interface (audio)
   0x09, 0x04, 0x01, 0x00, 0x02, 0x01, 0x03, 0x00, 0x00, // Interface 1
   0x07, 0x24, 0x01, 0x00, 0x01, 0x41, 0x00,             // CS Interface (midi)
   0x06, 0x24, 0x02, 0x01, 0x01, 0x00,                   //   IN  Jack 1 (emb)
   0x06, 0x24, 0x02, 0x02, 0x02, 0x00,                   //   IN  Jack 2 (ext)
   0x09, 0x24, 0x03, 0x01, 0x03, 0x01, 0x02, 0x01, 0x00, //   OUT Jack 3 (emb)
   0x09, 0x24, 0x03, 0x02, 0x04, 0x01, 0x01, 0x01, 0x00, //   OUT Jack 4 (ext)
   0x09, 0x05, 0x01, 0x02, 0x40, 0x00, 0x00, 0x00, 0x00, // Endpoint OUT
   0x05, 0x25, 0x01, 0x01, 0x01,                         //   CS EP IN  Jack
   0x09, 0x05, 0x81, 0x02, 0x40, 0x00, 0x00, 0x00, 0x00, // Endpoint IN
   0x05, 0x25, 0x01, 0x01, 0x03                         //   CS EP OUT Jack
 };

rom struct{byte bLength;byte bDscType;word string[1];}sd000={
 sizeof(sd000),DSC_STR,0x0409};

 rom struct{byte bLength;byte bDscType;word string[12];}sd001={
 sizeof(sd001),DSC_STR,
 'B','l','u','e','d','o','t',' ','I','n','c','.'};

 rom struct{byte bLength;byte bDscType;word string[12];}sd002={
 sizeof(sd002),DSC_STR,
 'P','i','c','U','S','B','-','M','I','D','I'};

rom const unsigned char *rom USB_CD_Ptr[]={&cfg01,&cfg01};
rom const unsigned char *rom USB_SD_Ptr[]={&sd000,&sd001,&sd002};
