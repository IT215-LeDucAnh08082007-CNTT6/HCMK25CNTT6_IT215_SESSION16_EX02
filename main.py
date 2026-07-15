"""  
    Lỗi 1: Lỗi đồng bộ ngược trong quan hệ 1 - N
        - Vị trí: employees = relationship("Employee", back_populates="department_id")
        - Nguyên nhân: back_populates yêu cầu phải trỏ đến tên thuộc tính quan hệ (relationship) ở class đối diện, chứ không phải tên cột khóa ngoại (Column).
        - Cách sửa: 
            employees = relationship("Employee", back_populates="department_id") -> employees = relationship("Employee", back_populates="department")

    Lỗi 2: Lỗi cấu hình collection trong quan hệ 1-1
        - Vị trí: employee = relationship("Employee", back_populates="device")
        - Nguyên nhân: Mặc định, hàm relationship() trong SQLAlchemy sẽ coi mọi liên kết là quan hệ 1-N (trả về một danh sách/list các đối tượng).
        - Cách sửa:
            device = relationship("Device", back_populates="employee") -> device = relationship("Device", back_populates="employee", uselist=False)

    Lỗi 3: Thiếu cấu hình bảng trung gian secondary trong quan hệ N-N
        - Vị trí: 
            projects = relationship("Project", back_populates="employees")
            employees = relationship("Employee", back_populates="projects")
        - Nguyên nhân: Đối với quan hệ Nhiều - Nhiều, SQLAlchemy không thể tự động biết dữ liệu liên kết được lưu ở đâu nếu không có bảng trung gian.
        - Cách sửa:
            projects = relationship("Project", secondary= employee_project, back_populates="employees")
            employees = relationship("Employee", secondary= employee_project, back_populates="projects")            
"""



from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base # Giả định Base

employee_project = Table(
    "employee_project", 
    Base.metadata,
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True)
)

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="employees")
    
    device = relationship("Device", back_populates="employee", uselist=False)
    
    projects = relationship("Project", secondary= employee_project, back_populates="employees")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(50), unique=True, nullable=False)

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", back_populates="device")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)

    employees = relationship("Employee", secondary= employee_project, back_populates="projects")