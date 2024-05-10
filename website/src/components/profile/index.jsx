import React from "react";
import styles from "./index.module.css";
import placeholder from "../../assets/user.png";

const Profile = () => {
    return (
        <div className={styles.avatar}>
            <img src={placeholder} alt="avatar" />
        </div>
    )
}

export default Profile;