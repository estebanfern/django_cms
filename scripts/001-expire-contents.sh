#!/bin/bash

#crontab -e
#* * * * * /root/update_content.sh >> /root/update_content.log 2>&1

psql -U tu_usuario -d tu_base_de_datos -c "UPDATE public.CONTENT c SET state = 'inactive' WHERE state = 'publish' AND date_expire <= NOW();"
