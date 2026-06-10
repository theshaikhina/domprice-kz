interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: Array<{ value: string; label: string }>;
  required?: boolean;
}

export const Select = ({ label, options, required, id, value, ...props }: SelectProps) => {
  return (
    <div className="form-group">
      <label htmlFor={id} className="form-label">
        {label}
        {required && <span className="required">*</span>}
      </label>

      <select
        id={id}
        className={`form-select ${!value ? 'placeholder' : ''}`}
        value={value}
        required={required}
        {...props}
      >
        <option value="" disabled hidden>
          Выберите {label.toLowerCase()}
        </option>

        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};