<?php
//Login php
if(isset($_POST['submit'])){
    //Take inputs from submission
    $email = $_POST['email'];
    $passcode = $_POST['password'];

}

//connect to DB
define("host", "localhost:3307");
define("db_user", "root");
define("pass", "");
define("db", "users");

$con2 = mysqli_connect(host, db_user, null, db);



if (!$con2){
    die("Connection to DB failed" . mysqli_connect_error());

}


//Read emails and passwords from DB
$query = "SELECT email, password from info";

$login_check = mysqli_query($con2, $query);
//check for match while iterating through table
if($login_check->num_rows > 0){
   
    while($row = mysqli_fetch_assoc($login_check)){
        if($email == $row["email"] && $passcode == $row["password"]){
            echo "login found";
            header("location: sessstart.php");
            break;
        }
        else{
            echo "Username and Password not found";
            header("location: badlogin.html");
        }
        
    }
}
else{
    echo "not found";
    header("location:badlogin.html");
}


mysqli_close($con2);


?>