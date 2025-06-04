CREATE TABLE user_devices (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT NOT NULL,
    device_token VARCHAR(255) NOT NULL,
    platform     ENUM('android','ios','web') NOT NULL,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_device (device_token),
    FOREIGN KEY (user_id) REFERENCES user_auth(id) ON DELETE CASCADE
); 