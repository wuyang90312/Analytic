1. Build up the pre_config.sh:
    - Upgrade the system
    - Download the mySQL server
    - Secure-check the server
    - Download mySQL module of Python


2. Finish Config_Table.sql:
    - Construct database DataAnalytics: Data || Analytics

        #--------------------------------------DESIGNS-----------------------------------------#
        Condition 1:
            The table "Data" is given and initially empty, BUT it only has the column of "INFO".
        Solution:
            Attach another table, "Analytics", to store a further info
    
             __________________________________
            *                                  *
            * table: "Data"                    *
            * column:| INFO |                  *
            *__________________________________*

        Where ID is just an integer up to 10,000,000.

        Condition 2:
            Require table holding a count per minute of information by domain name.

             ________________________________________
            *                                        *
            * table: "Analytics"                     *
            * column:|DOMAIN|COUNT|PERCENT|DATE      *
            *________________________________________*

        Where COUNT record the total number of domains so far.


3. Algorithm in python:
        Therefore, if we want to calculate the growth rate, we can compute:

            OFFSET = COUNT(NOW) - COUNT(30 days ago)
            PERCENT = OFFSET / COUNT(NOW)
            EXTREMITY: COUNT(30 days ago) = 0 => growth rate = 100%

        Basic data structure:
        1. dictionary store all of the number by different domains as keys. 
        2. Once, the date changes, upload this dictionary upto database and then restart the step1.
