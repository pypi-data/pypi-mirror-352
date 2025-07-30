import React from 'react';
import { Paper, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Summary } from '../common/types';

interface SummaryComponentProps {
  summary: Summary[];
  loading: boolean;
}

const SummaryComponent: React.FC<SummaryComponentProps> = (
  props
): JSX.Element => {
  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'project', headerName: 'Project', width: 130 },
    { field: 'podName', headerName: 'Pod name', width: 150 },
    { field: 'usage', headerName: 'Usage (time)', type: 'number', width: 130 },
    {
      field: 'cost',
      headerName: 'ToDate Cost ($)',
      type: 'number',
      width: 130
    },
    { field: 'month', headerName: 'Month', width: 60, align: 'center' },
    { field: 'year', headerName: 'Year', width: 60, align: 'center' },
    { field: 'lastUpdate', headerName: 'Updated', width: 270 }
  ];

  const paginationModel = { page: 0, pageSize: 10 };

  return (
    <React.Fragment>
      <Typography variant="h6" gutterBottom>
        Monthly costs and usages to date
      </Typography>
      <Paper sx={{ p: 2, boxShadow: 3, borderRadius: 2, mb: 2 }}>
        <DataGrid
          autoHeight
          rows={props.summary}
          columns={columns}
          loading={props.loading}
          initialState={{
            pagination: { paginationModel },
            columns: {
              columnVisibilityModel: {
                id: false
              }
            }
          }}
          pageSizeOptions={[10, 20, 30]}
          disableRowSelectionOnClick
          sx={{ border: 0 }}
        />
      </Paper>
    </React.Fragment>
  );
};

export default SummaryComponent;
