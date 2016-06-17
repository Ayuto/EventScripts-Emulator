//=========== (C) Copyright 2005 Mattie Casper All rights reserved. ===========
//
// Events triggered by the EventScripts plugin


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

"eventscriptsevents"
{
	"es_map_start"
	{
		"mapname"	"string"   	// name of the map
	}
	"es_scriptpack_register"
	{
		// this runs after the scriptpack is actually registered
		"scriptpack"	"string" 	// name of the script pack being unregistered
	}
	"es_scriptpack_unregister"
	{
		// this runs before the scriptpack is actually unregistered
		"scriptpack"	"string" 	// name of the script pack being unregistered
	}
	"es_player_validated"
	{
		// fired when a client is authenticated
		"name"		"string" 	// username
		"networkid"	"string"	// networkID
	}
	"es_player_setting"
	{
		// fired when a client changed one/several replicated cvars (name etc)
		"userid"	"short" 	// username
	}
	"es_client_command"			// a game event, name may be 32 charaters long
	{
		"userid"	"short"   	// user ID who issued the command
		"command"	"string" 	// name of the command
		"commandstring"	"string"	// text of the command after the commandname
	}
	"es_player_chat"            // a public player chat
	{
		"teamonly"      "bool"          // true if team only chat
		"userid"        "short"         // chatting player
		"text"          "string"        // chat text
	} 
	"es_player_variable"            // a player variable
	{
		"userid"        "short"         // userid's convar
		"status"        "string"        // status of the query
		"variable"      "string"        // name of the variable
		"value"         "string"        // value of the variable
	} 

}
