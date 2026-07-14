# PHẦN 1: BÁO CÁO LỖI LOGIC NGHIỆP VỤ (trace luồng và phát hiện lỗi khóa liên kết)
"""
-----------------------------------------------------------------------------------------------------------------------------------------
STT | Lỗi Logic Phát Hiện                   | Kết Quả Thực Tế                 | Kết Quả Mong Đợi               | Nguyên Nhân Gây Lỗi TRONG CODE CŨ
----|---------------------------------------|---------------------------------|--------------------------------|---------------------------------------------------------
1   | Kiểm tra trùng hồ sơ bị sai trường   | Trả về 201 Created. Cho phép    | Phải trả về lỗi 409 Conflict   | Code cũ so sánh nhầm mã hồ sơ (`profile["id"]`) với
    | dữ liệu (Nhầm giữa id và user_id).    | tạo nhiều hồ sơ cho cùng 1 User.| và chặn không cho tạo tiếp.    | mã người dùng: `if profile["id"] == user_id`.
----|---------------------------------------|---------------------------------|--------------------------------|---------------------------------------------------------
2   | Hoàn toàn thiếu điều kiện kiểm tra    | Trả về 201 Created. Vẫn tạo     | Phải trả về lỗi 404 Not Found  | Hàm `create_profile` không hề check sự tồn tại của
    | người dùng tồn tại trong hệ thống.    | hồ sơ cho `user_id = 999`.      | vì User không tồn tại.         | `user_id` trong danh sách `users` trước khi xử lý.
----|---------------------------------------|---------------------------------|--------------------------------|---------------------------------------------------------
3   | Kiểm tra trùng số điện thoại bị sai   | Trả về 201 Created. Cho phép    | Phải trả về lỗi 409 Conflict   | Ràng buộc check trùng số điện thoại bị bóp hẹp trong
    | phạm vi nghiệp vụ hệ thống.           | trùng số điện thoại ở các User khác| nếu số điện thoại đã tồn tại.  | cùng 1 User: `and profile["user_id"] == user_id`.
-----------------------------------------------------------------------------------------------------------------------------------------

DỮ LIỆU MINH CHỨNG CHO CÁCH TRACE TEST CASE:
- Test Case Lỗi 1 (Tạo nhiều hồ sơ): Gọi POST `/users/1/profile` với JSON {"full_name": "An Bản 2", "phone": "0901000002"} -> Lọt qua và tạo thành công hồ sơ thứ hai cho User 1.
- Test Case Lỗi 2 (User không tồn tại): Gọi POST `/users/999/profile` với JSON {"full_name": "Ghost", "phone": "0901000003"} -> Tạo thành công hồ sơ ảo.
- Test Case Lỗi 3 (Trùng số điện thoại): Gọi POST `/users/2/profile` với JSON {"full_name": "Bình", "phone": "0901000001"} (Trùng số của An) -> Tạo thành công.
"""

# PHẦN 2: SOURCE CODE ĐÃ ĐƯỢC VÁ LỖI LOGIC HOÀN CHỈNH (QUAN HỆ 1-1 CHUẨN)

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class UserProfileCreate(BaseModel):
    full_name: str
    phone: str
    address: str | None = None

users = [
    {
        "id": 1,
        "username": "nguyenvanan",
        "email": "an@gmail.com"
    },
    {
        "id": 2,
        "username": "tranthibinh",
        "email": "binh@gmail.com"
    }
]

profiles = [
    {
        "id": 10,
        "full_name": "Nguyễn Văn An",
        "phone": "0901000001",
        "address": "Hà Nội",
        "user_id": 1
    }
]

@app.get("/users")
def get_users():
    return users

@app.get("/profiles")
def get_profiles():
    return profiles

@app.post(
    "/users/{user_id}/profile",
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    user_id: int,
    profile_data: UserProfileCreate
):
    user_exists = next((u for u in users if u["id"] == user_id), None)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )

    existing_profile = next(
        (
            profile
            for profile in profiles
            if profile["user_id"] == user_id
        ),
        None
    )
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Người dùng đã có hồ sơ"
        )

    duplicated_phone = next(
        (
            profile
            for profile in profiles
            if profile["phone"] == profile_data.phone
        ),
        None
    )
    if duplicated_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Số điện thoại đã được sử dụng"
        )

    new_id = max([p["id"] for p in profiles], default=0) + 1
    new_profile = {
        "id": new_id,
        "full_name": profile_data.full_name,
        "phone": profile_data.phone,
        "address": profile_data.address,
        "user_id": user_id
    }
    
    profiles.append(new_profile)
    return new_profile