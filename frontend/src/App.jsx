import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

export default function App() {
  const [students, setStudents] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  
  const emptyForm = { student_id: '', full_name: '', dob: '', class_name: '', arm: '', password: '' };
  const [form, setForm] = useState(emptyForm);
  const [image, setImage] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => { loadStudents(); }, []);

  const loadStudents = async () => {
    const res = await axios.get('http://localhost:5000/api/students');
    setStudents(res.data);
  };

  const handleEditClick = (student) => {
    setIsEditing(true);
    setForm({
      student_id: student.student_id,
      full_name: student.full_name,
      dob: student.dob || '',
      class_name: student.class_name,
      arm: student.arm || '',
      password: '' // Require typing a password to confirm changes
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = new FormData();
      Object.keys(form).forEach(key => data.append(key, form[key]));
      if (image) data.append('image', image);

      if (isEditing) {
        await axios.put(`http://localhost:5000/api/students/${form.student_id}`, data);
        alert("Student updated successfully!");
      } else {
        await axios.post('http://localhost:5000/api/students', data);
        alert("Student registered successfully!");
      }
      
      loadStudents();
      setForm(emptyForm);
      setImage(null);
      setIsEditing(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
      
    } catch (error) {
      const msg = error.response?.data?.error || "Could not connect to server.";
      alert((isEditing ? "Update failed: " : "Registration failed: ") + msg);
    }
  };

  const handleDelete = async (id) => {
    await axios.delete(`http://localhost:5000/api/students/${id}`);
    loadStudents();
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>{isEditing ? "Edit Student" : "Register Student"}</h2>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '10px', maxWidth: '300px' }}>
        <input value={form.student_id} placeholder="Student ID" onChange={e => setForm({...form, student_id: e.target.value})} required disabled={isEditing} />
        <input value={form.full_name} placeholder="Full Name" onChange={e => setForm({...form, full_name: e.target.value})} required />
        <input value={form.dob} type="date" onChange={e => setForm({...form, dob: e.target.value})} required />
        <input value={form.class_name} placeholder="Class" onChange={e => setForm({...form, class_name: e.target.value})} required />
        <input value={form.arm} placeholder="Arm (Optional)" onChange={e => setForm({...form, arm: e.target.value})} />
        <input value={form.password} type="password" placeholder="Password" onChange={e => setForm({...form, password: e.target.value})} required />
        <input ref={fileInputRef} type="file" onChange={e => setImage(e.target.files[0])} required={!isEditing} />
        
        <button type="submit">{isEditing ? "Save Changes" : "Register"}</button>
        {isEditing && (
          <button type="button" onClick={() => { setIsEditing(false); setForm(emptyForm); }}>Cancel Edit</button>
        )}
      </form>

      <h2>Student List</h2>
      <ul>
        {students.map(s => (
          <li key={s.student_id} style={{ marginBottom: '10px' }}>
            {s.full_name} ({s.student_id}) - {s.class_name} 
            <button onClick={() => handleEditClick(s)} style={{ marginLeft: '10px', color: 'blue' }}>Edit</button>
            <button onClick={() => handleDelete(s.student_id)} style={{ marginLeft: '10px', color: 'red' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}