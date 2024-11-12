to setup the system:

#execute the folloeing commands
nmcli con add type wifi ifname wlan0 con-name Sara autoconnect yes ssid Sara
nmcli con modify Sara 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
nmcli con modify Sara wifi-sec.key-mgmt wpa-psk
nmcli con modify Sara wifi-sec.psk Hs24Sara1234$
nmcli con up Sara

crontab -e 
	add the following: @reboot /home/luca/Sara/autostartMain.sh
