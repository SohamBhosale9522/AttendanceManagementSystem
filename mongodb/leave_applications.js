db = db.getSiblingDB("AttendanceManagement");

db.createCollection("leave_applications");

db.leave_applications.insertMany([
  {
    application_id: "LA001",
    student_roll_no: "IT001",
    student_name: "Aarav Sharma",
    leave_type: "Medical",
    reason: "Fever and medical checkup",
    start_date: ISODate("2026-10-26T00:00:00Z"),
    end_date: ISODate("2026-10-27T00:00:00Z"),
    status: "Pending",
    applied_at: new Date()
  },
  {
    application_id: "LA002",
    student_roll_no: "IT002",
    student_name: "Priya Patil",
    leave_type: "Personal",
    reason: "Family function",
    start_date: ISODate("2026-10-28T00:00:00Z"),
    end_date: ISODate("2026-10-28T00:00:00Z"),
    status: "Approved",
    applied_at: new Date()
  },
  {
    application_id: "LA003",
    student_roll_no: "IT003",
    student_name: "Rohan Deshmukh",
    leave_type: "Medical",
    reason: "Dental appointment",
    start_date: ISODate("2026-10-29T00:00:00Z"),
    end_date: ISODate("2026-10-29T00:00:00Z"),
    status: "Rejected",
    applied_at: new Date()
  },
  {
    application_id: "LA004",
    student_roll_no: "IT004",
    student_name: "Sneha Kulkarni",
    leave_type: "Personal",
    reason: "Personal work at home",
    start_date: ISODate("2026-10-30T00:00:00Z"),
    end_date: ISODate("2026-10-30T00:00:00Z"),
    status: "Pending",
    applied_at: new Date()
  },
  {
    application_id: "LA005",
    student_roll_no: "IT005",
    student_name: "Aditya Joshi",
    leave_type: "Medical",
    reason: "Fever",
    start_date: ISODate("2026-10-31T00:00:00Z"),
    end_date: ISODate("2026-10-31T00:00:00Z"),
    status: "Approved",
    applied_at: new Date()
  }
]);

// 1. Display all leave applications
db.leave_applications.find();

// 2. Find pending leave applications
db.leave_applications.find({ status: "Pending" });

// 3. Regex: find student names beginning with A
db.leave_applications.find({
  student_name: { $regex: "^A", $options: "i" }
});

// 4. Find medical leave applications
db.leave_applications.find({ leave_type: "Medical" });

// 5. Count applications for each status
db.leave_applications.aggregate([
  {
    $group: {
      _id: "$status",
      total_applications: { $sum: 1 }
    }
  },
  { $sort: { total_applications: -1 } }
]);

// 6. Count applications by leave type
db.leave_applications.aggregate([
  {
    $group: {
      _id: "$leave_type",
      total_applications: { $sum: 1 }
    }
  }
]);

// 7. Display pending applications, newest first
db.leave_applications.find({ status: "Pending" })
  .sort({ applied_at: -1 });

// 8. Approve a leave application
db.leave_applications.updateOne(
  { application_id: "LA001" },
  { $set: { status: "Approved" } }
);

// 9. Verify the updated application
db.leave_applications.findOne({ application_id: "LA001" });
