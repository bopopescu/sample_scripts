 var mysql = require('mysql');

 var connection = mysql.createConnection({

   host : 'controller',
   user : 'expostack',
   password : 'BSoniC',
   port : 3306,
   database : 'expo_cinder'
 });

connection.connect( function(error) {
  if(error) throw error;
  console.log("Connected to database");
});

module.exports=connection;
