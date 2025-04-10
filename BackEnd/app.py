from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the React frontend

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_grades.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # Secret key for session management
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes_teaching = db.relationship('Class', backref='teacher', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_type': self.user_type,
            'created_at': self.created_at.isoformat()
        }
        
        if self.user_type == 'student':
            data['graduation_year'] = None
        elif self.user_type == 'teacher':
            data['department'] = self.department
            
        return data

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    class_code = db.Column(db.String(10), unique=True, nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    capacity = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='class', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'class_code': self.class_code,
            'class_name': self.class_name,
            'description': self.description,
            'capacity': self.capacity,
            'teacher_id': self.teacher_id,
            'teacher_name': f"{self.teacher.first_name} {self.teacher.last_name}",
            'enrolled_count': len(self.enrollments)
        }

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    grade = db.Column(db.Float, nullable=True)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'class_id', name='_student_class_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'class_id': self.class_id,
            'grade': self.grade,
            'enrollment_date': self.enrollment_date.isoformat()
        }

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'password', 'email', 'first_name', 'last_name', 'user_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        user_type=data['user_type']
    )
        
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User registered successfully', 'user_id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    # Store user info in session
    session['user_id'] = user.id
    session['user_type'] = user.user_type
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

# Class Routes
@app.route('/api/classes', methods=['GET'])
def get_all_classes():
    """Get all classes with enrollment counts"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    classes = Class.query.all()
    return jsonify({
        'success': True,
        'classes': [cls.to_dict() for cls in classes]
    }), 200

@app.route('/api/classes/<int:class_id>', methods=['GET'])
def get_class_details(class_id):
    """Get details of a specific class"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    cls = Class.query.get(class_id)
    if not cls:
        return jsonify({'success': False, 'message': 'Class not found'}), 404
    
    class_data = cls.to_dict()
    
    # If user is a teacher and teaches this class, include student details
    if session['user_type'] == 'teacher' and cls.teacher_id == session['user_id']:
        students = []
        for enrollment in cls.enrollments:
            student = User.query.get(enrollment.student_id)
            students.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'enrollment_id': enrollment.id,
                'grade': enrollment.grade
            })
        class_data['students'] = students
    
    return jsonify({
        'success': True,
        'class': class_data
    }), 200

@app.route('/api/classes', methods=['POST'])
def create_class():
    """Create a new class (teachers only)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if session['user_type'] != 'teacher':
        return jsonify({'success': False, 'message': 'Only teachers can create classes'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['class_code', 'class_name', 'capacity']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Check if class code already exists
    if Class.query.filter_by(class_code=data['class_code']).first():
        return jsonify({'success': False, 'message': 'Class code already exists'}), 400
    
    # Create new class
    new_class = Class(
        class_code=data['class_code'],
        class_name=data['class_name'],
        description=data.get('description'),
        capacity=data['capacity'],
        teacher_id=session['user_id']
    )
    
    try:
        db.session.add(new_class)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Class created successfully',
            'class': new_class.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Teacher Routes
@app.route('/api/teacher/classes', methods=['GET'])
def get_teacher_classes():
    """Get classes taught by the logged-in teacher"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if session['user_type'] != 'teacher':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    classes = Class.query.filter_by(teacher_id=session['user_id']).all()
    return jsonify({
        'success': True,
        'classes': [cls.to_dict() for cls in classes]
    }), 200

@app.route('/api/teacher/grades/<int:enrollment_id>', methods=['PUT'])
def update_grade(enrollment_id):
    """Update a student's grade (teachers only)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if session['user_type'] != 'teacher':
        return jsonify({'success': False, 'message': 'Only teachers can update grades'}), 403
    
    data = request.get_json()
    if 'grade' not in data:
        return jsonify({'success': False, 'message': 'Grade is required'}), 400
    
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'success': False, 'message': 'Enrollment not found'}), 404
    
    # Verify teacher teaches this class
    if enrollment.class_.teacher_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        enrollment.grade = data['grade']
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Grade updated successfully',
            'enrollment': enrollment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Student Routes
@app.route('/api/student/classes', methods=['GET'])
def get_student_classes():
    """Get classes enrolled by the logged-in student"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if session['user_type'] != 'student':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    enrollments = Enrollment.query.filter_by(student_id=session['user_id']).all()
    
    classes = []
    for enrollment in enrollments:
        class_data = enrollment.class_.to_dict()
        class_data['grade'] = enrollment.grade
        classes.append(class_data)
    
    return jsonify({
        'success': True,
        'classes': classes
    }), 200

@app.route('/api/student/enroll', methods=['POST'])
def enroll_in_class():
    """Enroll a student in a class"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if session['user_type'] != 'student':
        return jsonify({'success': False, 'message': 'Only students can enroll in classes'}), 403
    
    data = request.get_json()
    if 'class_id' not in data:
        return jsonify({'success': False, 'message': 'Class ID is required'}), 400
    
    # Check if class exists
    cls = Class.query.get(data['class_id'])
    if not cls:
        return jsonify({'success': False, 'message': 'Class not found'}), 404
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=session['user_id'],
        class_id=data['class_id']
    ).first()
    
    if existing_enrollment:
        return jsonify({'success': False, 'message': 'Already enrolled in this class'}), 400
    
    # Check if class is full
    if len(cls.enrollments) >= cls.capacity:
        return jsonify({'success': False, 'message': 'Class has reached maximum capacity'}), 400
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=session['user_id'],
        class_id=data['class_id']
    )
    
    try:
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Enrolled successfully',
            'enrollment': enrollment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Helper function to create demo data
def create_demo_data():
    """Create demo data for testing"""
    # Check if data already exists
    if User.query.count() > 0:
        return "Demo data already exists"
    
    try:
        # Create teachers
        teacher1 = User(
            username="teacher1",
            email="jsmith@school.edu",
            first_name="John",
            last_name="Smith",
            user_type="teacher",
        )
        teacher1.set_password("password123")
        
        teacher2 = User(
            username="teacher2",
            email="jdoe@school.edu",
            first_name="Jane",
            last_name="Doe",
            user_type="teacher",
        )
        teacher2.set_password("password123")
        
        db.session.add(teacher1)
        db.session.add(teacher2)
        db.session.commit()
        
        # Create students
        student1 = User(
            username="proy",
            email="proy3@ucmerced.edu",
            first_name="Parthib",
            last_name="Parthib",
            user_type="student",
        )
        student1.set_password("proy")
        
        student2 = User(
            username="student2",
            email="bbrown@school.edu",
            first_name="Bob",
            last_name="Brown",
            user_type="student",
        )
        student2.set_password("password123")
        
        student3 = User(
            username="student3",
            email="cdavis@school.edu",
            first_name="Charlie",
            last_name="Davis",
            user_type="student"
        )
        student3.set_password("password123")
        
        db.session.add(student1)
        db.session.add(student2)
        db.session.add(student3)
        db.session.commit()
        
        # Create classes
        math101 = Class(
            class_code="MATH101",
            class_name="Introduction to Algebra",
            description="Basic algebraic concepts for beginners",
            capacity=30,
            teacher_id=teacher1.id
        )
        
        math201 = Class(
            class_code="MATH201",
            class_name="Advanced Calculus",
            description="Calculus for science and engineering students",
            capacity=25,
            teacher_id=teacher1.id
        )
        
        sci101 = Class(
            class_code="SCI101",
            class_name="Introduction to Biology",
            description="Basic principles of biology and life sciences",
            capacity=35,
            teacher_id=teacher2.id
        )
        
        sci201 = Class(
            class_code="SCI201",
            class_name="Chemistry Fundamentals",
            description="Basic chemistry concepts and lab work",
            capacity=20,
            teacher_id=teacher2.id
        )
        
        db.session.add(math101)
        db.session.add(math201)
        db.session.add(sci101)
        db.session.add(sci201)
        db.session.commit()
        
        # Create enrollments
        enrollments = [
            Enrollment(student_id=student1.id, class_id=math101.id, grade=85.5),
            Enrollment(student_id=student1.id, class_id=sci101.id, grade=92.0),
            Enrollment(student_id=student2.id, class_id=math101.id, grade=78.5),
            Enrollment(student_id=student2.id, class_id=sci201.id),
            Enrollment(student_id=student3.id, class_id=math201.id),
            Enrollment(student_id=student3.id, class_id=sci101.id)
        ]
        
        for enrollment in enrollments:
            db.session.add(enrollment)
            
        db.session.commit()
        return "Demo data created successfully"
    
    except Exception as e:
        db.session.rollback()
        return f"Error creating demo data: {str(e)}"


# For direct execution
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(create_demo_data())
    app.run(debug=True)


    # Error Checks

    # if 'user_id' not in session:
    #     return jsonify({'success': False, 'message': 'Authentication required'}), 401
    #
    # if session['user_type'] != 'PROPER_USER':
    #     return jsonify({'success': False, 'message': 'Only PROPER_USER can enroll in classes'}), 403
    #
    # if 'class_id' not in data:
    #     return jsonify({'success': False, 'message': 'Class ID is required'}), 400
    #
    # Check if class exists
    # if not cls:
    #     return jsonify({'success': False, 'message': 'Class not found'}), 404
    #
    # Sesseion
    # except Exception as e:
    # db.session.rollback()
    # return jsonify({'success': False, 'message': str(e)}), 500