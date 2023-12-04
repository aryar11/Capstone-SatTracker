<?php
//Find account to create new password

//Set variables when button is clicked
if(isset($_POST['submit'])){
    $username = $_POST['username'];
    $security_answer = $_POST['security_answer'];
    $new_password = $_POST['new_password'];
    $conf_new_pass = $_POST['newconfirm_password'];
}

/*Connect to the DB 
define("host", "localhost:3307");
define("db_user", "root");
define("pass", "");
define("db", "users"); */
define("host", "sattrack.ckiq4qoeqhbu.us-east-2.rds.amazonaws.com");
define("db_user", "admin");
define("pass", "SatTracker23");
define("db", "users");


$con3 = mysqli_connect(host, db_user, null, db);

if (!$con3){
    die("Connection to DB failed" . mysqli_connect_error());

}

//Check that passwords entered match
if($new_password != $conf_new_pass){
    echo"Password don't match!";
    header("location: error.html");
    $err = true;
}


//Selecting columns from table
$query2 = "SELECT name, username, security_question, security_answer from info";

//Query the table
$user_check = mysqli_query($con3, $query2);
if($user_check->num_rows > 0){
   
    while($row = mysqli_fetch_assoc($user_check)){
        //Check if email matches input
        if($username == $row["username"] && $security_answer == $row["security_answer"]){
            //Copy data from database
            $name = $row["name"];
            $username = $row["username"];
            $security_question = $row["security_question"];
            $security_answer = $row["security_answer"];

            //Delete account from DB
            $deleteold = "DELETE from info where username='".mysqli_real_escape_string($con3, $username)."'";
            $del = mysqli_query($con3, $deleteold);

            //Insert new password with account info into table
            $holdsql = "INSERT INTO info (name, username, password, security_question, security_answer) VALUES ('".mysqli_real_escape_string($con3, $name)."', '".mysqli_real_escape_string($con3, $username)."', '".mysqli_real_escape_string($con3, $new_password)."', '".mysqli_real_escape_string($con3, $security_question)."', '".mysqli_real_escape_string($con3, $security_answer)."')";
            $rs2 = mysqli_query($con3, $holdsql);
            if($rs2) {
                echo "entries added!";
                header("location: sessstart.php");
            }
            break;
        }
        else{
            echo "Username not found";
            header("location: error.html");
        }
        
    }
}

else{
    echo "not found";
    header("location:error.html");
}


mysqli_close($con3);


?>