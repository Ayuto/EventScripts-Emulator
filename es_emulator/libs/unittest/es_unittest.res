//=========== (C) Copyright 2005 Mattie Casper All rights reserved. ===========
//
// Events triggered by unittests


// No spaces in event names, max length 32
// All strings are case sensitive
// total game event byte length must be < 1024
//
// valid data key types are:
//   none   : value is not networked
//   string : a zero terminated string
//   bool   : unsigned int, 1 bit
//   byte   : unsigned int, 8 bit
//   short  : signed int, 16 bit
//   long   : signed int, 32 bit
//   float  : float, 32 bit

"unittestevents"
{
	"es_event_unittest"
	{
		"teamonly"      "bool"          // true if team only chat
		"userid"        "short"         // chatting player
		"text"          "string"        // chat text
	}
	"es_unittest_done"
	{
		"ignored"      "bool"          // ignored
	} 
}
