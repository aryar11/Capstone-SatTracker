
<?php
/*require_once "config.php";
require_once "session.php";

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['submit'])){
    $fullname = trim($_POST['name']);
    $email = trim($_POST['email']);
    $password = trim($_POST['password']);
    $confirm_password = trim($_POST["confirm_password"]);
    $password_hash = password_hash($password, PASSWORD_BCRYPT);

    if($query = $con->prepare("SELECT * FROM info WHERE email = ?")) {
        $error = '';

    $query->bind_param('s', $email);
    $query->execute();

    $query->store_result();

        if($query->num_rows > 0) {
            $error .= '<p class="error">The email adress is already registered!</p>';
        } else{
            if (strlen($password ) < 6) {
                $error.= '<p class="error">The password is too short.</p>'; 
            }
            if(empty($confirm_password)) {
                $error .= '<p class="error">Please enter confirm password.</p>';
            }
            else{
                if(empty($error) && ($password != $confirm_password)) {
                    $error .= '<p class="success">Your registration was unsuccessful</p>';
                }
            }

            if(empty($error)) {
                $insertQuery = $con->prepare("INSERT INTO info (name, email, password) VALUES (?, ?, ?);");
                $insertQuery->bind_param("sss", $fullname, $email, $password_hash);
                $result = $insertQuery->execute();
                if($insertQuery) {
                    $error .= '<p class="success"> Your registration was successful!</p>';
                } else{
                    $error .= '<p class="error"> Something wrong</p>';
                }
            }
        } 
    }
    $query->close();
    $insertQuery->close();
    

    mysqli_close($con);

}
?>*/

