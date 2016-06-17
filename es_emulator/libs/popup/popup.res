// Events triggered by Popup python library


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

"popup"
{
	"popup_display"								// when the popup is displayed
	{
		"userid"				"short"				// the userid of the receiver
		"popup_name"		"string"				// name of the popup
		"popup_timeout"	"float"				// the time until the popup expires
	}
	"popup_select"									// when the user confirms the popup
	{
		"userid"				"short"				// the userid of the popup user
		"popup_name"		"string"				// name of the popup
		"popup_choice"		"short"				// the menu option chosen
	}
}