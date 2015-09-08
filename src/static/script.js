function handleEntry(form_id, act) {
	
	document.getElementById(act + "_" + form_id).blur();
	
	var form_obj = document.getElementById(form_id);
	var isconfirmed = window.confirm("do you really want to " + act + " entry " + form_id);
	
	if (isconfirmed == true) {
		
		if (act == "delete") {
			
			form_obj.action="{{ url_for('delete_entry') }}";
			form_obj.submit();
			
		} else if (act == "modify") {
			
			alert("Under developing...");
		}
	}
}