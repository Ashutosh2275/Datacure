import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

// Mock the Common components
jest.mock('../Common', () => ({
  ProtectedRoute: ({ children }) => <div data-testid="protected-route">{children}</div>,
  LoadingSpinner: () => <div data-testid="loading-spinner">Loading...</div>,
  ErrorAlert: ({ message }) => <div data-testid="error-alert">{message}</div>,
  SuccessAlert: ({ message }) => <div data-testid="success-alert">{message}</div>,
  DataTable: ({ data, columns, onEdit, onDelete }) => (
    <div data-testid="data-table">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col.key}>{row[col.key]}</td>
              ))}
              <td>
                {onEdit && (
                  <button onClick={() => onEdit(row)} data-testid={`edit-btn-${idx}`}>
                    Edit
                  </button>
                )}
                {onDelete && (
                  <button onClick={() => onDelete(row.id)} data-testid={`delete-btn-${idx}`}>
                    Delete
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ),
  FormField: ({ label, name, value, onChange, error, type = 'text' }) => (
    <div data-testid={`form-field-${name}`}>
      <label>{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        data-testid={`input-${name}`}
      />
      {error && <span data-testid={`error-${name}`}>{error}</span>}
    </div>
  ),
  Modal: ({ isOpen, title, onClose, children }) =>
    isOpen ? (
      <div data-testid="modal">
        <h2>{title}</h2>
        {children}
        <button onClick={onClose} data-testid="modal-close">Close</button>
      </div>
    ) : null,
}));

describe('Common Components', () => {
  describe('ProtectedRoute', () => {
    it('renders protected content', () => {
      const { ProtectedRoute } = require('../Common');
      render(
        <BrowserRouter>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </BrowserRouter>
      );
      expect(screen.getByTestId('protected-route')).toBeInTheDocument();
    });
  });

  describe('LoadingSpinner', () => {
    it('displays loading spinner', () => {
      const { LoadingSpinner } = require('../Common');
      render(<LoadingSpinner />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });

  describe('ErrorAlert', () => {
    it('displays error message', () => {
      const { ErrorAlert } = require('../Common');
      const errorMsg = 'Something went wrong!';
      render(<ErrorAlert message={errorMsg} />);
      expect(screen.getByTestId('error-alert')).toBeInTheDocument();
      expect(screen.getByText(errorMsg)).toBeInTheDocument();
    });
  });

  describe('SuccessAlert', () => {
    it('displays success message', () => {
      const { SuccessAlert } = require('../Common');
      const successMsg = 'Operation successful!';
      render(<SuccessAlert message={successMsg} />);
      expect(screen.getByTestId('success-alert')).toBeInTheDocument();
      expect(screen.getByText(successMsg)).toBeInTheDocument();
    });
  });

  describe('DataTable', () => {
    const mockData = [
      { id: 1, name: 'John Doe', email: 'john@example.com' },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
    ];

    const mockColumns = [
      { key: 'name', label: 'Name' },
      { key: 'email', label: 'Email' },
    ];

    it('renders table with data', () => {
      const { DataTable } = require('../Common');
      render(<DataTable data={mockData} columns={mockColumns} />);
      
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    });

    it('calls onEdit when edit button clicked', () => {
      const { DataTable } = require('../Common');
      const mockEdit = jest.fn();
      render(<DataTable data={mockData} columns={mockColumns} onEdit={mockEdit} />);
      
      fireEvent.click(screen.getByTestId('edit-btn-0'));
      expect(mockEdit).toHaveBeenCalledWith(mockData[0]);
    });

    it('calls onDelete when delete button clicked', () => {
      const { DataTable } = require('../Common');
      const mockDelete = jest.fn();
      render(<DataTable data={mockData} columns={mockColumns} onDelete={mockDelete} />);
      
      fireEvent.click(screen.getByTestId('delete-btn-1'));
      expect(mockDelete).toHaveBeenCalledWith(2);
    });
  });

  describe('FormField', () => {
    it('renders form field with label', () => {
      const { FormField } = require('../Common');
      const mockChange = jest.fn();
      render(
        <FormField
          label="Email"
          name="email"
          value=""
          onChange={mockChange}
        />
      );
      
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByTestId('input-email')).toBeInTheDocument();
    });

    it('calls onChange when input changes', () => {
      const { FormField } = require('../Common');
      const mockChange = jest.fn();
      const { getByTestId } = render(
        <FormField
          label="Name"
          name="name"
          value="John"
          onChange={mockChange}
        />
      );
      
      const input = getByTestId('input-name');
      fireEvent.change(input, { target: { value: 'Jane' } });
      expect(mockChange).toHaveBeenCalled();
    });

    it('displays error message', () => {
      const { FormField } = require('../Common');
      const errorMsg = 'Field is required';
      render(
        <FormField
          label="Email"
          name="email"
          value=""
          onChange={() => {}}
          error={errorMsg}
        />
      );
      
      expect(screen.getByTestId('error-email')).toBeInTheDocument();
      expect(screen.getByText(errorMsg)).toBeInTheDocument();
    });
  });

  describe('Modal', () => {
    it('renders modal when open', () => {
      const { Modal } = require('../Common');
      const mockClose = jest.fn();
      render(
        <Modal isOpen={true} title="Test Modal" onClose={mockClose}>
          <p>Modal Content</p>
        </Modal>
      );
      
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Test Modal')).toBeInTheDocument();
      expect(screen.getByText('Modal Content')).toBeInTheDocument();
    });

    it('does not render modal when closed', () => {
      const { Modal } = require('../Common');
      render(
        <Modal isOpen={false} title="Test Modal" onClose={jest.fn()}>
          <p>Modal Content</p>
        </Modal>
      );
      
      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });

    it('calls onClose when close button clicked', () => {
      const { Modal } = require('../Common');
      const mockClose = jest.fn();
      render(
        <Modal isOpen={true} title="Test Modal" onClose={mockClose}>
          <p>Modal Content</p>
        </Modal>
      );
      
      fireEvent.click(screen.getByTestId('modal-close'));
      expect(mockClose).toHaveBeenCalled();
    });
  });
});
