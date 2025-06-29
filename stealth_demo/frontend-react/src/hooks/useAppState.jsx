import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { apiService } from '../services/apiService'

// 初始狀態
const initialState = {
  keys: [],
  addresses: [],
  dsks: [],
  txMessages: [],
  traceKey: null,
  selectedKeyIndex: -1,
  selectedAddrIndex: -1,
  selectedDSKIndex: -1,
  setupComplete: false,
  currentParamFile: null,
  paramFiles: [],
  loading: {},
  errors: {}
}

// Action types
const ACTION_TYPES = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_PARAM_FILES: 'SET_PARAM_FILES',
  SET_SETUP_COMPLETE: 'SET_SETUP_COMPLETE',
  SET_TRACE_KEY: 'SET_TRACE_KEY',
  ADD_KEY: 'ADD_KEY',
  SET_KEYS: 'SET_KEYS',
  ADD_ADDRESS: 'ADD_ADDRESS',
  ADD_DSK: 'ADD_DSK',
  ADD_TX_MESSAGE: 'ADD_TX_MESSAGE',
  SET_SELECTED_KEY: 'SET_SELECTED_KEY',
  SET_SELECTED_ADDRESS: 'SET_SELECTED_ADDRESS',
  SET_SELECTED_DSK: 'SET_SELECTED_DSK',
  RESET_ALL: 'RESET_ALL'
}

// Reducer (因為太長，我會分段給您)