<?php

    // GroupID 453639
    // LastPaid 608767

    // Get the auth token.  If you've already made this call just use the same token from before.
    $apikey = '';
    $login  = '';
    $pass   = '';
    $url    = 'https://ocns.memberclicks.net/services/auth';
    $data   = 'apiKey='.$apikey.'&username='.$login.'&password='.$pass;
    $verbose = true;
    $current_year = "2018";

    $group_list   = array("OCNS Board", "Student Member", "Faculty Member", "Basic Contact", "Postdoc Member");
    $user_email   = 'pierre.yger@inserm.fr';
    $nb_abstracts = 0;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);

    $httpHeaders[] = "Accept: application/json";
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $httpHeaders );

    $result = curl_exec($ch);

    // Parse the json result
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($result, $header_size);
    $jsonResult = json_decode( $body );
    curl_close($ch);

    $token = $jsonResult->token;
    // end getting the token.  Sample code begins below

    // **** Get User ****
    $url = 'https://ocns.memberclicks.net/services/user?searchText='.$user_email;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $httpHeaders[] = "Accept: application/json";
    $httpHeaders[] = "Authorization: ".$token;
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $httpHeaders );

    $result = stripslashes(curl_exec($ch));

    // Parse the json result
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($result, $header_size);
    $jsonResult = json_decode( $body, true);

    if (array_key_exists('userId', $jsonResult['user'])) {

        //Only one user is found, so we are happy
        $userId = array($jsonResult['user']['userId']);
        if ($verbose) {
            echo "We found the user ".$userId[0]."<br />";
        }
    }
    else {
        // Either we do not have a single user, either multiple users are registered with the
        // same contact email (sad, but true). In this case, we need to loop
        if (count($jsonResult['user']) == 0) {
            echo "User not registered? <br />";
        }
        else {
            if ($verbose) {
                echo "Several users with the same email <br />";
            }
            $userId = array();
            foreach ($jsonResult['user'] as $key => $value) {
               $userId = array_merge($userId, array($value['userId']));
            }
        }
    }
    curl_close($ch);

    foreach ($userId as $key => $id) {
        // Getting the value of the Group attribute, as a string
        $url = 'https://ocns.memberclicks.net/services/user/' . $id .'/attribute/453639';
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $httpHeaders );
        $result = stripslashes(curl_exec($ch));
        $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $body = substr($result, $header_size);
        $jsonResult = json_decode( $body, true);
        $group = $jsonResult['attData'];
        curl_close($ch);

        // Getting the value of the RegistrationYer attribute, as a string
        $url = 'https://ocns.memberclicks.net/services/user/' . $id .'/attribute/609323';
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $httpHeaders );
        $result = stripslashes(curl_exec($ch));
        $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $body = substr($result, $header_size);
        $jsonResult = json_decode( $body, true);
        $registration = $jsonResult['attData'];
        curl_close($ch);

        if (in_array($group, $group_list)) {
            if ($verbose) {
                echo "User ".$user_email." is a valid user from group ".$group."<br />";
            }
            //If the user exists, we check if he has registered for this year
            if ($registration == $current_year) {
                if ($verbose) {
                    echo "User ".$user_email." is indeed registered for year ".$current_year."  <br />";
                }
                //If yes, he is able to submit 1 abstract as a Basic Contact
                //or two otherwise
                if ($group == "Basic Contact") {
                    $nb_abs = 1;
                }
                else {
                    $nb_abs = 2;
                }
        // If we found a valid regisration, leading to more abstracts for the user, then we
        // update the value (this is because of possible multiple users with same email)
        if ($nb_abs > $nb_abstracts) {
            $nb_abstracts = $nb_abs;
        }
            }
        }
    }
    if ($verbose) {
    echo "User ".$user_email." is getting ".$nb_abstracts." abstracts <br />";
    }
?>