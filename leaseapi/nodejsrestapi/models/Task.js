var db=require('../dbconnection');
//var mysqlTimestamp = moment().utc().format('hh:mm:ss')
//var mysqlTimestamp = new Date();
//mysqlTimestamp = moment(mysqlTimestamp).format("YYYY-MM-DD HH:mm:ss");
var Task={

getAllTasks:function(callback){

return db.query("Select * from expo_nova.lease_active_vms",callback);

},
getTaskById:function(id,callback){

    return db.query("select * from expo_nova.lease_active_vms where hostname =?",[id],callback);
},
addTask:function(Task,callback){
  
 console.log("inside service");
   console.log(Task.Id);
var mysqlTimestamp = new Date();
return db.query("Insert into expo_nova.lease_active_vms values(?,?,?,?,?,?,?)",[Task.Hostname,mysqlTimestamp,Task.leasedays,'success','days',Task.Owner,Task.Ipaddress],callback);
//return db.query("insert into task(Id,Title,Status) values(?,?,?)",[Task1.Id,Task1.Title,Task1.Status],callback);
},
deleteTask:function(id,callback){
    return db.query("delete from expo_nova.lease_active_vms where hostname=?",[id],callback);
},
updateTask:function(id,Task,callback){
var mysqlTimestamp = new Date();
    return  db.query("update expo_nova.lease_active_vms SET created_on = ?,leasedays = ?,owner = ?,ipaddress = ?  where hostname =?",[mysqlTimestamp,Task.leasedays,Task.Owner,Task.Ipaddress,id],callback);
},
deleteAll:function(item,callback){

var delarr=[];
   for(i=0;i<item.length;i++){

       delarr[i]=item[i].Id;
   }
   return db.query("delete from expo_nova.lease_active_vms where hostname  in (?)",[delarr],callback);
}
};
module.exports=Task;
