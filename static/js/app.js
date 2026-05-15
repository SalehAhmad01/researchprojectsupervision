document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => new bootstrap.Tooltip(el));
    document.querySelectorAll('.progress-dynamic').forEach((el) => {
        el.style.width = `${el.dataset.progress || 0}%`;
    });

    const roleField = document.querySelector('[data-register-field="role"] select');
    const studentIdWrapper = document.querySelector('[data-register-field="student_id"]');
    const staffIdWrapper = document.querySelector('[data-register-field="staff_id"]');
    const toggleRegistrationIds = () => {
        if (!roleField || !studentIdWrapper || !staffIdWrapper) {
            return;
        }
        const isStudent = roleField.value === 'student';
        studentIdWrapper.classList.toggle('d-none', !isStudent);
        staffIdWrapper.classList.toggle('d-none', isStudent);
        studentIdWrapper.querySelector('input').disabled = !isStudent;
        staffIdWrapper.querySelector('input').disabled = isStudent;
    };
    if (roleField) {
        roleField.addEventListener('change', toggleRegistrationIds);
        toggleRegistrationIds();
    }
});
