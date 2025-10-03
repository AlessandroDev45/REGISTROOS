import React from 'react';
import { CheckCircleIcon, XCircleIcon } from 'lucide-react'; // Assuming Lucide icons are available, or use SVG if not

const AprovacaoColaboradoresTab: React.FC = () => {
  return (
    <div className="w-full max-w-7xl mx-auto bg-white shadow-lg rounded-xl border border-gray-200 overflow-hidden">
      <div className="p-8 bg-gradient-to-r from-indigo-50 via-blue-50 to-cyan-50 border-b border-blue-200">
        <div className="flex items-center mb-4">
          <div className="p-2 bg-blue-100 rounded-full mr-4">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-7.303a6.5 6.5 0 01-6.5-6.5m0 0a6.5 6.5 0 00-6.5 6.5m6.5 0H17a3 3 0 11-6 0H9m10.5 7.303a6.5 6.5 0 01-6.5-6.5m0 0a6.5 6.5 0 00-6.5 6.5m6.5 0H17" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">
            Aprovação de Colaboradores - LABORATORIO DE ENSAIOS ELETRICOS
          </h2>
        </div>
        <p className="text-base text-gray-600 italic font-medium">
          Gerencie solicitações (Filtrado por setor: LABORATORIO DE ENSAIOS ELETRICOS)
        </p>
      </div>
      <div className="p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
              <tr>
                <th className="px-8 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-200">
                  Nome
                </th>
                <th className="px-8 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-200">
                  Email
                </th>
                <th className="px-8 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-200">
                  Setor
                </th>
                <th className="px-8 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr className="hover:bg-blue-50 transition-colors duration-200 even:bg-gray-50">
                <td className="px-8 py-6 whitespace-nowrap text-base font-semibold text-gray-900 border-r border-gray-200">
                  JAO  DAS 
                </td>
                <td className="px-8 py-6 whitespace-nowrap text-base text-gray-600 border-r border-gray-200">
                  jaodascouves@teste.com
                </td>
                <td className="px-8 py-6 whitespace-nowrap text-base text-gray-600 border-r border-gray-200">
                  N/A
                </td>
                <td className="px-8 py-6 whitespace-nowrap text-base font-semibold">
                  <button className="mr-3 inline-flex items-center px-4 py-3 border border-transparent text-sm font-medium rounded-lg shadow-md text-white bg-green-500 hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 transform hover:scale-105">
                    <CheckCircleIcon className="w-4 h-4 mr-2" />
                    Aprovar
                  </button>
                  <button className="inline-flex items-center px-4 py-3 border border-transparent text-sm font-medium rounded-lg shadow-md text-white bg-red-500 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200 transform hover:scale-105">
                    <XCircleIcon className="w-4 h-4 mr-2" />
                    Rejeitar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        {/*
          Adicione aqui um indicador se houver mais dados, mas mantendo o conteúdo original
          Por exemplo: se vazio, mostrar empty state, mas como há dados, omitir
        */}
      </div>
    </div>
  );
};

export default AprovacaoColaboradoresTab;
