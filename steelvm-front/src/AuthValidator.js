import axios from "axios";

export default function CheckAuth(){
    try {
        axios.get("http://localhost:8000/api/auth/validate-token",{
            headers:{
                Authorization:"Bearer " + localStorage.getItem("access_token")
            }
        })
        return true
    }
    catch (e){
        return false;
    } 
}